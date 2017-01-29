"""
Definition of views.
"""

from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
#from app.models import UnreadMessage
from app.models import Patient, Doctor
import json

from .forms import QueryPatientsForm
from .forms import PatientNotesForm
from .forms import SignupForm 
from django.forms.utils import ErrorList

from django.contrib.auth.models import User


import logging
#import MySQLdb
from redcap import Project, RedcapError
import urllib

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient


class DivErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_spans()
    def as_spans(self):
        if not self: return ''
        return ''.join(['<div><span class="control-label">%s</span></div>' % e for e in self])


def dashboard(request):
    """Renders the dashboard page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    unread_messages_patients = []

    unread_messages_patients = Patient.objects.filter(unread_messages__gt=0)

    context = {
        'title':'Dashboard',
        'year':datetime.now().year,
        'unread_messages': unread_messages_patients,
    }

    """
    URL = 'https://hcbredcap.com.br/api/'
    TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

    project = Project(URL, TOKEN)

    for field in project.metadata:
        print "%s (%s) => %s" % (field['field_name'],field['field_type'], field['field_label'])

    data = project.export_records()
    for d in data:
        print d
        """


    return render(
        request,
        'app/dashboard.html',
        context
    )


def login_redirect(request, **kwargs):
    # Checks to see if user is logged in. If so, redirect to dashboard page.
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return auth_views.login(request, **kwargs)

def patients(request):
    """Renders the patients page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    print "request.user.username:", request.user.username

    patient_results = []

    if request.method == 'GET':
        print "[views.searchPatients] got GET request"

        # Get "patient_query" url param
        patient_query = request.GET.get("patient_query", '')
        print "patient_query:", patient_query

        doctor = Doctor.objects.get(user=request.user)
        print "doctor:", doctor

        if patient_query == '':
            # No specific patient query. Show all patients
            patient_results = doctor.patients.all()

        else:
            # Actual query. Fetch close matches.
            #longer_matches = doctor.patients.filter(full_name__search=patient_query)
            patient_results = doctor.patients.filter(full_name__icontains=patient_query)
            # Trigram matches will exclude results that are "farther" distance away.
            #tri_matches = doctor.patients.filter(full_name__lower__trigram_similar=patient_query)

            #patient_results = list(set(longer_matches).union(set(tri_matches)))

    else:
        print "else"

    query_patients_form = QueryPatientsForm()

    context = {
        'title': 'Patients',
        'message': 'List of patients.',
        'year': datetime.now().year,
        'patient_results': patient_results,
        'form': query_patients_form,
    }

    return render(
        request,
        'app/patients.html',
        context
    )


def patient_profile(request):
    """Renders the patient profile page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    patient_id = request.GET['u_id']
    print "patient_id:", patient_id

    patient = Patient.objects.get(u_id = patient_id)

    notes_form = PatientNotesForm()

    context = {
        'title': 'Patient Profile',
        'message': 'Patient profile.',
        'year': datetime.now().year,
        'patient': patient,
        'notes_form': notes_form,
    }

    return render(
        request,
        'app/patient_profile.html',
        context
    )

def signup(request):
    """Renders the patients page."""
    assert isinstance(request, HttpRequest)

    signup_form = SignupForm(error_class=DivErrorList)

    if request.method == 'POST':
        signup_form = SignupForm(request.POST, error_class=DivErrorList)

        if signup_form.is_valid():
            full_name = signup_form.cleaned_data['full_name']
            username = signup_form.cleaned_data['username']
            password = signup_form.cleaned_data['password_1']
            role = signup_form.cleaned_data['doctor_patient_choice']

            user = User.objects.create(username=username, password=password)

            if role == 'patient':
                # Create User and Patient object.
                patients_doctor_username = signup_form.cleaned_data['patients_doctor_username']
                patient = Patient.objects.create(user=user, u_id=10, full_name=full_name)
                Doctor.objects.get(user=User.objects.get(username=patients_doctor_username)).patients.add(patient)
            else:
                # Create User and Doctor object.
                doctor = Doctor.objects.create(user=user, u_id=10, full_name=full_name)

            return HttpResponseRedirect("/signup-success/")


    context = {
        'title': 'Sign Up',
        'year': datetime.now().year,
        'form': signup_form,
    }

    return render(
        request,
        'app/sign_up.html',
        context
    )

def signup_success(request):
    """Renders the page after a user has successfully signed up."""
    assert isinstance(request, HttpRequest)


    context = {
        'title': 'Sign Up',
        'year': datetime.now().year,
    }

    return render(
        request,
        'app/sign_up_success.html',
        context
    )


def messages(request):
    """Renders the messages page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    channels = []
    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        print "channel", c.friendly_name
        for m in c.members.list():
            print m.identity
            # Assuming that all twilio identities are based off of usernames
            if m.identity == request.user.username:
                # str() needed to get rid of u'hello' when escaping the string to javascript.
                channel_json = {
                    'sid': str(c.sid),
                    'unique_name': str(c.unique_name),
                    'friendly_name': str(c.friendly_name),
                }
                channels.append(channel_json)
                break

        """
        print "== Channel =="
        print "\tsid: ", c.sid
        print "\tunique_name: ", c.unique_name
        print "\tfriendly_name: ", c.friendly_name
        print "\tattributes: ", c.attributes
        print "\tlinks: ", c.links
        print "\tmembers:"
        for m in c.members.list():
            print "\t\t", m.identity
        """

    patients = Patient.objects.all()
    
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, request.user.username)
    endpoint = "PalliAssist:" + request.user.username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    context = {
        'title':'Messages',
        'message':'Send messages.',
        'year':datetime.now().year,
        'patients': patients,
        'channels': channels,
        'token': token,
    }

    return render(
        request,
        'app/messages.html',
        context
    )

"""
Saves a message to the REDCap database.
"""
def save_message(request):
    assert isinstance(request, HttpRequest)

    print request

    sender = request.GET['sender']
    channel = request.GET['channel']
    content = request.GET['content']
    content_type = request.GET['type']
    time_sent = request.GET['time_sent']

    print "saveMessage:"
    print sender, channel, content, content_type, time_sent

    """
    db = MySQLdb.connect(host="us-cdbr-azure-southcentral-f.cloudapp.net", user="b811fcf3c52d36", passwd="91e7ba1e", db="palliative")
    cur = db.cursor()

    sender_id = cur.execute("SELECT id FROM palliative.login WHERE username = '" + sender + "';")
    print sender_id

    result = cur.execute("INSERT INTO palliative.messages VALUES(" + str(sender_id) + ", '" + channel + "', '" + content + "', '" + content_type + "', " + str(time_sent) + ");")
    print result

    cur.close()

    db.commit()
    db.close()
    """

    URL = 'https://hcbredcap.com.br/api/'
    TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

    #project = Project(URL, TOKEN)

    for field in settings.REDCAP_USER_PROJECT.metadata:
        print "%s (%s) => %s" % (field['field_name'],field['field_type'], field['field_label'])

    data = settings.REDCAP_USER_PROJECT.export_records()
    for d in data:
        print d

    d = data[0]
    d['content'] = content
    d['content_type'] = content_type
    d['channel'] = channel
    d['time_sent'] = time_sent

    response = settings.REDCAP_USER_PROJECT.import_records(data)
    print response['count']
        

    
    return JsonResponse({})

"""
Gets an access token for Twilio IP messaging. Called by messages.js.
"""
def token(request):
    assert isinstance(request, HttpRequest)

    # create a randomly generated username for the client
    identity = request.GET['identity']

    # <unique app>:<user>:<device>
    endpoint = "PalliAssist:" + identity + ":mobile"

    # Create access token with credentials
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, identity)

    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    # COMMENTED CAUSE FLASK THING - Return token info as JSON 
    #return jsonify(identity=identity, token=token.to_jwt())
    return JsonResponse({'identity': identity, 'token': token.to_jwt()})

def save_notes(request):
    """
    Saves notes about patients. POST request from 
    PatientNotesForm on the patient profile page. 
    jQuery runs when save button is clicked.
    """
    assert isinstance(request, HttpRequest)

    doctor_notes = request.POST['notes']
    print "doctor_notes:", doctor_notes
    print "doctor_notes:", urllib.quote(doctor_notes)
    patient_id = request.POST['u_id']

    patient = Patient.objects.get(u_id=patient_id)
    patient.doctor_notes = urllib.quote(doctor_notes)
    patient.save()

    return JsonResponse({})

def test_url(request):
    """ NOT IN USE """
    assert isinstance(request, HttpRequest)

    notification = settings.TWILIO_NOTIFY_CLIENT.notify.services(settings.TWILIO_NOTIFY_SERVICE_SID).notifications.create(
            tag="all",
            body="Hello World from PalliAssist"
    )

    print notification

    return JsonResponse({'notification': notification})

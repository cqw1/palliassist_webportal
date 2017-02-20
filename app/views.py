"""
Definition of views.
"""

from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.template import RequestContext
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
#from app.models import UnreadMessage
#from app.models import Patient, Doctor
from app.models import *
from django.core import serializers
from django.utils import timezone

import json
import datetime
import pytz

from .forms import QueryPatientsForm
from .forms import PatientNotesForm
from .forms import SignupForm 
from django.forms.utils import ErrorList

from django.contrib.auth.models import User


import logging
#import MySQLdb
from redcap import Project, RedcapError
#import urllib

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
        'year':datetime.datetime.now().year,
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
        'year': datetime.datetime.now().year,
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

    patient_id = request.GET['sid']
    print "patient_id:", patient_id

    patient_obj = Patient.objects.get(sid=patient_id)
    patient_obj.next_appointment = convertDateTimeToMillis(patient_obj.next_appointment)

    notes_form = PatientNotesForm()

    ### Messages tab.
    channels = []
    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        if c.unique_name == patient_obj.user.username:
            print "selected channel", c.friendly_name, c.sid
            channel_json = {
                'sid': str(c.sid),
                'unique_name': str(c.unique_name),
                'friendly_name': str(c.friendly_name),
            }
            channels.append(channel_json)
            break

    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, request.user.username)
    endpoint = "PalliAssist:" + request.user.username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    ### ESAS tab.
    esas_objects = ESASSurvey.objects.filter(patient=patient_obj)

    for esas in esas_objects:
        esas.created_date = convertDateTimeToMillis(esas.created_date)

    esas_json = serializers.serialize("json", esas_objects)

    """
    for esas in esas_objects:
        temp_esas = {}
        #temp_esas["created_date"] = (esas.created_date.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
        temp_esas["created_date"] = convertDateTimeToMillis(esas.created_date)
        temp_questions = []
        for q in esas.questions.all():
            temp_questions.append({"question": str(q.question), "answer": q.answer})

        temp_esas["questions"] = temp_questions
        temp_esas["primary_key"] = esas.pk;
        esas_surveys.append(temp_esas)
    """



    ### Pain tab.
    pain_objects = PainSurvey.objects.filter(patient=patient_obj)
    for pain in pain_objects:
        pain.created_date = convertDateTimeToMillis(pain.created_date)


    ### Medication tab.
    medications = Medication.objects.filter(patient=patient_obj)
    for medication in medications:
        medication.created_date = convertDateTimeToMillis(medication.created_date)


    context = {
        'title': 'Patient Profile',
        'message': 'Patient profile.',
        'year': datetime.datetime.now().year,
        'patient': patient_obj,
        'notes_form': notes_form,
        'medications': medications,
        'esas_objects': esas_objects,
        'esas_json': esas_json,
        'pain_objects': pain_objects,
        'pain_width': 207,
        'pain_height': 400,
        'channels': channels, 
        'token': token, # Twilio token for messaging tab.
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
                patient = Patient.objects.create(user=user, sid=10, full_name=full_name)
                Doctor.objects.get(user=User.objects.get(username=patients_doctor_username)).patients.add(patient)
            else:
                # Create User and Doctor object.
                doctor = Doctor.objects.create(user=user, sid=10, full_name=full_name)

            return HttpResponseRedirect("/signup-success/")


    context = {
        'title': 'Sign Up',
        'year': datetime.datetime.now().year,
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
        'year': datetime.datetime.now().year,
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

    """
    How to delete a channel:
    """
    """
    # Delete current demo channel.
    demo_channel = settings.TWILIO_IPM_SERVICE.channels.get(sid="CH775a5cc2b8ef42db8362f101e305569a")
    response = demo_channel.delete()
    print "delete Demo Channel:", response   # response = True on success.

    # Recreate demo channel.
    new_channel = settings.TWILIO_IPM_SERVICE.channels.create(friendly_name="Demo Channel", unique_name="Demo Channel", type="public")
    new_channel.members.create(identity=request.user.username)
    """
    
    """
    patient0 = "patient0"
    # patient0 channel sid="CHd4c969e1d91946aeb1ebde3fa5cb85a2"
    new_channel = settings.TWILIO_IPM_SERVICE.channels.create(unique_name=patient0, friendly_name=patient0, type="private")
    new_channel.members.create(identity=request.user.username)
    new_channel.members.create(identity=patient0)
    """



    channels = []
    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        for m in c.members.list():
            #print m.identity
            # Assuming that all twilio identities are based off of usernames
            if m.identity == request.user.username:
                # str() needed to get rid of u'hello' when escaping the string to javascript.
                print "selected channel", c.friendly_name, c.sid
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
        'year':datetime.datetime.now().year,
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
    #return JsonResponse({'identity': identity, 'token': token})

def save_notes(request):
    """
    Saves notes about patients. POST request from 
    PatientNotesForm on the patient profile page. 
    jQuery runs when save button is clicked.
    """
    assert isinstance(request, HttpRequest)

    """
    doctor_notes = request.POST['notes']
    print "doctor_notes:", doctor_notes
    print "doctor_notes:", urllib.quote(doctor_notes)
    patient_id = request.POST['sid']

    patient = Patient.objects.get(sid=patient_id)
    patient.doctor_notes = urllib.quote(doctor_notes)
    patient.save()
    """

    return JsonResponse({})

def create_channel(request):
    """
    Saves notes about patients. POST request from 
    PatientNotesForm on the patient profile page. 
    jQuery runs when save button is clicked.
    """
    assert isinstance(request, HttpRequest)

    print request.POST['channel_name']
    channel_name = request.POST['channel_name']

    new_channel = settings.TWILIO_IPM_SERVICE.channels.create(friendly_name=channel_name, type="private")
    new_channel.members.create(identity=request.user.username)

    print new_channel
    print new_channel.type
    print new_channel.friendly_name
    print new_channel.unique_name

    return JsonResponse({})

@csrf_exempt
def fcm(request):
    """
    Handle FCM requests from mobile.
    Format described in Meeting Minutes Feb 2, 2017
    """
    assert isinstance(request, HttpRequest)

    fcm_action = request.POST["action"]
    print "fcm_action", fcm_action

    fcm_timestamp = request.POST["timestamp"] # milliseconds
    dt_unaware = datetime.datetime.fromtimestamp(int(fcm_timestamp)/1000.0)
    dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
    print "dt_aware", dt_aware 

    fcm_type = request.POST["type"]
    print "fcm_type", fcm_type 

    fcm_patient = request.POST["patient"] # TODO hardcoded to patient0 right now 
    patient_obj = User.objects.get(username=fcm_patient).patient
    print "patient_obj", patient_obj 

    #return JsonResponse({"action": fcm_action, "timestamp": fcm_timestamp, "type": fcm_type, "questions": fcm_questions})


    if fcm_action == "REQUEST":
        # TODO
        pass
    elif fcm_action == "SAVE":
        if fcm_type == "ESAS":
            fcm_questions = request.POST["questions"] # comes in string.
            questions = json.loads(fcm_questions) # JSON object.
            print "questions", questions

            esas = ESASSurvey.objects.create(patient=patient_obj, created_date=dt_aware)

            for q in questions:
                temp_q = ESASQuestion.objects.create(question=q["question"], answer=q["answer"])
                print temp_q
                esas.questions.add(temp_q)

            esas.save()
            print "esas", esas

        elif fcm_type == "PAIN":
            pain = PainSurvey.objects.create(created_date=dt_aware, patient=patient_obj, width=int(request.POST["width"]), height=int(request.POST["height"]))

            # int(float()) to get around parsing a string with a decimal to an int
            pain_point = PainPoint.objects.create(x=int(float(request.POST["x"])), y=int(float(request.POST["y"])), intensity=int(request.POST["intensity"]))

            print int(request.POST["width"])
            print int(request.POST["height"])
            print int((float(request.POST["x"])))
            print int((float(request.POST["y"])))
            print int((float(request.POST["intensity"])))

            print "pain_point", pain_point 
            pain.points.add(pain_point)
            print "points", pain.points.all()

            pain.save()
            print "pain", pain

            """
            fcm_points = request.POST["points"] # comes in string.
            points = json.loads(fcm_points) # JSON object.

            for p in points:
                temp_p = PainPoint.objects.create(x=int(p["x"]), y=int(p["y"]), intensity=int(p["intensity"]))
                print temp_p
                pain.points.add(temp_p)

            pain.save()
            print pain
            """

        elif fcm_type == "MEDICATION":
            # TODO
            pass
        elif fcm_type == "CUSTOM":
            # TODO
            pass
        else:
            print "Unknown request type", fcm_type 
    else:
        print "Unknown request action", fcm_action 

    return render(request, 'app/blank.html')

def convertDateTimeToMillis(dt):
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000


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
from app.models import *
from django.core import serializers
from django.utils import timezone

import json
import datetime
import pytz
import os

from .forms import *
from django.forms.utils import ErrorList

from django.contrib.auth.models import User

"""
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage.blob import ContentSettings 
"""


import logging
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
        'query_patients_form': query_patients_form,
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

    patient_pk = request.GET['pk']
    print "patient_pk:", patient_pk  

    patient_obj = Patient.objects.get(pk=patient_pk)

    notes_form = PatientNotesForm()
    create_notification_form = CreateNotificationForm()
    create_medication_form = CreateMedicationForm()
    upload_image_form = UploadImageForm()

    ### Notifications tab.
    notifications = Notification.objects.filter(patient=patient_obj)


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
    esas_millis = ESASSurvey.objects.filter(patient=patient_obj)

    for esas in esas_millis:
        esas.created_date = convert_datetime_to_millis(esas.created_date)

    esas_json = serializers.serialize("json", esas_millis)

    ### Pain tab.
    pain_objects = PainSurvey.objects.filter(patient=patient_obj)
    for pain in pain_objects:
        for point in pain.front_points.all():
            point.rgb = 255.0 / ((((point.intensity + 1.0) / 11.0) * 2.0) + 1.0)
            point.save()


    ### Medication tab.
    medications = Medication.objects.filter(patient=patient_obj)

    context = {
        'title': 'Patient Profile',
        'message': 'Patient profile.',
        'year': datetime.datetime.now().year,
        'patient': patient_obj,
        'notes_form': notes_form,
        'create_notification_form': create_notification_form,
        'create_medication_form': create_medication_form,
        'upload_image_form': upload_image_form,
        'notifications': notifications,
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
                patient = Patient.objects.create(user=user, full_name=full_name)
                Doctor.objects.get(user=User.objects.get(username=patients_doctor_username)).patients.add(patient)
            else:
                # Create User and Doctor object.
                doctor = Doctor.objects.create(user=user, full_name=full_name)

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
    """ Renders the messages page. """
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

    """
    # Delete all channels that aren't Demo Channel or patient0 channel
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        if c.sid == "CHd4c969e1d91946aeb1ebde3fa5cb85a2":
            # Don't delete patient0 channel
            pass
        elif c.sid == "CHe75c920bb94c449da5fba883aa64db6c":
            # Don't delete demo channel
            pass
        else:
            c.delete()
    """

    """
    # Update friendly name of channel
    patient0_channel = settings.TWILIO_IPM_SERVICE.channels.get(sid="CHd4c969e1d91946aeb1ebde3fa5cb85a2")
    patient0_channel.update(friendly_name="Patient 0")
    """
        

    # Always allow the user to chat in the demo channel by adding to it if we haven't already been added.
    demo_channel = settings.TWILIO_IPM_SERVICE.channels.get(sid="CHe75c920bb94c449da5fba883aa64db6c")
    demo_json = {
        'sid': str(demo_channel.sid),
        'unique_name': str(demo_channel.unique_name),
        'friendly_name': str(demo_channel.friendly_name),
    }
    #demo_channel.update(unique_name="demochannel")
    member = demo_channel.members.create(identity=request.user.username)

    channels = []
        

    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        print "looking at", c.friendly_name, c.unique_name, c.sid
        for m in c.members.list():
            #print m.identity
            # Assuming that all twilio identities are based off of usernames
            if m.identity == request.user.username:
                # str() needed to get rid of u'hello' when escaping the string to javascript.
                print "selected channel", c.friendly_name, c.unique_name, c.sid
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
    upload_image_form = UploadImageForm()

    patients = Patient.objects.all()
    
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, request.user.username)
    endpoint = "PalliAssist:" + request.user.username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    context = {
        'title':'Messages',
        'message':'Send messages.',
        'upload_image_form': upload_image_form,
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


def save_message(request):
    """
    Saves a message to the REDCap database.
    """
    assert isinstance(request, HttpRequest)

    print request

    sender = request.GET['sender']
    channel = request.GET['channel']
    content = request.GET['content']
    content_type = request.GET['type']
    time_sent = request.GET['time_sent']

    print "saveMessage:"
    print sender, channel, content, content_type, time_sent

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

def token(request):
    """
    Gets an access token for Twilio IP messaging. Called by messages.js.
    """
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

def create_notification(request):
    """
    Creates a Notification model based on uer input.
    """
    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    Notification.objects.create(
            created_date=timezone.now(), 
            category=request.POST["category"], 
            text=request.POST["text"], 
            patient=patient_obj
    )

    return JsonResponse({})

def create_medication(request):
    """
    Creates a Medication model based on uer input.
    """
    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    medication = Medication.objects.create(
            created_date=timezone.now(),
            patient=patient_obj,
            name=request.POST["name"],
            form=request.POST["form"],
            dose=request.POST["dose"],
            posology=request.POST["posology"],
            rescue=request.POST["rescue"]
    )

    print medication

    return JsonResponse({})

def upload_image(request):

    success = False
    message = ""
    blob_name = ""
    container_name = ""

    patient_obj = User.objects.get(username=request.POST["username"]).patient
    print patient_obj

    if len(request.FILES.items()) > 0:
        for name, temp_image in request.FILES.items():
            image_obj = Image.objects.create(created_date=timezone.now(), patient=patient_obj, image=temp_image)


        container_name = patient_obj.user.username

        """
        settings.BLOCK_BLOB_SERVICE.create_container(container_name, public_access=PublicAccess.Container)
        blob_name = patient_obj.user.username + "_" + str(convert_datetime_to_millis(datetime.datetime.now()))
        settings.BLOCK_BLOB_SERVICE.create_blob_from_path(container_name, blob_name, image_obj.image.path, content_settings=ContentSettings(content_type='image/png'))
        """
        success = True

    else:
        message = "Error uploading image. Please try again."


    return JsonResponse({
        "success": success, 
        "message": message,
        "blob_name": blob_name,
        "container_name": container_name
    })

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

def handle_completed_medication(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a medication.
    """

    medication = Medication.objects.get(pk=data["pk"])

    # TODO. figure out how to handle this medication completed event

    print medication
    print medication.patient

    return JsonResponse({})

def handle_completed_pain(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a pain survey.
    """

    pain = PainSurvey.objects.create(created_date=dt, patient=patient_obj, width=int(data["width"]), height=int(data["height"]))

    for point in post["front"]["points"]:
        pain_point = PainPoint.objects.create(x=int(float(data["x"])), y=int(float(data["y"])), intensity=int(data["intensity"]))
        pain.front_points.add(pain_point)
        pain.save()

    for point in post["back"]["points"]:
        pain_point = PainPoint.objects.create(x=int(float(data["x"])), y=int(float(data["y"])), intensity=int(data["intensity"]))
        pain.back_points.add(pain_point)
        pain.save()

    print pain
    return JsonResponse({})

def handle_completed_ESAS(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a ESAS survey.
    """

    esas = ESASSurvey.objects.create(created_date=dt, patient=patient_obj)
    esas.pain = int(data["pain"])
    esas.fatigue = int(data["fatigue"])
    esas.nausea = int(data["nausea"])
    esas.depression = int(data["depression"])
    esas.anxiety = int(data["anxiety"])
    esas.drowsiness = int(data["drowsiness"])
    esas.appetite = int(data["appetite"])
    esas.well_being = int(data["well_being"])
    esas.lack_of_air = int(data["lack_of_air"])
    esas.insomnia = int(data["insomnia"])
    esas.pain = int(data["pain"])

    esas.fever = data["fever"]
    
    esas.constipated = data["constipated"]
    if data["constipated"] == "yes":
        esas.constipated_days = int(data["constipated_days"])
        esas.constipated_bothered = int(data["constipated_bothered"])

    esas.vomiting = data["vomiting"]
    if data["vomiting"] == "yes":
        esas.vomiting_count = int(data["vomiting_count"])

    esas.confused = data["confused"]

    esas.save()
    print esas


    return JsonResponse({})


@csrf_exempt
def mobile(request):
    """
    Handle FCM requests from mobile.
    Format described in Meeting Minutes Feb 2, 2017
    """
    assert isinstance(request, HttpRequest)

    print request.POST

    patient_username = request.POST["patient"] # TODO hardcoded to patient0 right now 
    patient_obj = User.objects.get(username=patient_username).patient
    print "patient_obj", patient_obj 


    event = request.POST["event"]

    if event == "COMPLETED":

        timestamp = request.POST["timestamp"] # milliseconds
        dt_unaware = datetime.datetime.fromtimestamp(int(timestamp)/1000.0)
        dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
        print "dt_aware", dt_aware 

        if request.POST["category"] == "MEDICATION":
            return handle_completed_medication(dt_aware, patient_obj, json.loads(request.POST["data"]))

        elif request.POST["category"] == "PAIN":
            return handle_completed_pain(dt_aware, patient_obj, json.loads(request.POST["data"]))

        elif request.POST["category"] == "ESAS":
            return handle_completed_ESAS(dt_aware, patient_obj, json.loads(request.POST["data"]))

    elif event == "LOGIN":
        if request.POST["category"] == "MEDICATION":
            return JsonResponse({
                'medications': serializers.serialize("json", Medication.objects.filter(patient=patient_obj))
            })

        elif request.POST["category"] == "NOTIFICATION":
            return JsonResponse({
                'notifications': serializers.serialize("json", Notification.objects.filter(patient=patient_obj))
            })

    # TODO. return an error.

    return render(request, 'app/blank.html')


@csrf_exempt
def sync_redcap(request):
    """ 
    Syncs all django models with the REDCap records.
    django primary_key in model == REDCap record_id in record.
    """

    medications = Medication.objects.all()
    
    medication_data = []
    for medication in medications:
        medication_data.append({
            "record_id": medication.pk,
            "name": medication.name,
            "form": medication.form,
            "dose": medication.dose,
            "posology": medication.posology,
            "rescue": medication.rescue
        })


    medication_response = settings.REDCAP_MEDICATION_PROJECT.import_records(medication_data)
    print "medication models:", len(medications)
    print "medication_response:", medication_response["count"]


    return JsonResponse({})




def convert_datetime_to_millis(dt):
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000





def admin_input(request):

    return render(
        request,
        'app/admin_input.html',
        {}
    )

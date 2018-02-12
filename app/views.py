"""
Definition of views.
"""

from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from app.models import *
from app.forms import *
from django.core import serializers
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _

import json
import datetime
import pytz
import os
import phonenumbers

from .forms import *
from django.forms.utils import ErrorList

from django.contrib.auth.models import User

from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage.blob import ContentSettings 


import logging
from redcap import Project, RedcapError
#import urllib

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient

from pyfcm import FCMNotification


class DivErrorList(ErrorList):
    def __unicode__(self):              # __unicode__ on Python 2
        return self.as_spans()
    def as_spans(self):
        if not self: return ""
        return "".join(['<div><span class="control-label">%s</span></div>' % e for e in self])


def dashboard(request):
    """Renders the dashboard page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("login"))

    unread_patients = []
    unread_patients = Patient.objects.filter(unread_messages__gt=0)

    # Maps patient object to a mapping of esas surveys with a symptom over 7
    # to the corresponding dashboard alert
    unordered_patient_esas_alert = {}
    ordered_patient_esas_alert = []
    esas_alerts = DashboardAlert.objects.filter(category=DashboardAlert.ESAS)

    sorted_esas = []
    for alert in esas_alerts:
        sorted_esas.append(ESASSurvey.objects.get(pk=alert.item_pk))

    # Sort esas by created_date
    sorted_esas.sort(key=lambda x: x.created_date, reverse=True)

    # Get all the patients, and related alerts and esas
    for esas in sorted_esas:
        alert = DashboardAlert.objects.get(category=DashboardAlert.ESAS, item_pk=esas.pk)

        if alert.patient not in unordered_patient_esas_alert.keys():
            unordered_patient_esas_alert[alert.patient] = ()

        # Do some conversions between tuples and lists cause lists cant be stored in dictionaries
        # and need to maintain order
        tup = unordered_patient_esas_alert[alert.patient]
        lst = list(tup)
        lst.append((esas, alert))
        unordered_patient_esas_alert[alert.patient] = tuple(lst)

    # Sort patients by full_name
    esas_patients = unordered_patient_esas_alert.keys()
    esas_patients.sort(key=lambda x: x.full_name)

    for patient in esas_patients:
        ordered_patient_esas_alert.append((patient, unordered_patient_esas_alert[patient]))

    # Maps patient object to a mapping of incomplete medication reports
    # to the corresponding dashboard alert
    unordered_patient_medication_alert = {}
    ordered_patient_medication_alert = []
    medication_alerts = DashboardAlert.objects.filter(category=DashboardAlert.MEDICATION)

    sorted_medication = []
    for alert in medication_alerts:
        sorted_medication.append(MedicationReport.objects.get(pk=alert.item_pk))

    # Sort medication by created date
    sorted_medication.sort(key=lambda x: x.created_date, reverse=True)

    # Get all the patients and related alerts and medication
    for medication in sorted_medication:
        alert = DashboardAlert.objects.get(category=DashboardAlert.MEDICATION, item_pk=medication.pk)

        if alert.patient not in unordered_patient_medication_alert.keys():
            unordered_patient_medication_alert[alert.patient] = ()

        # Do some conversions between tuples and lists cause lists cant be stored in dictionaries
        # and need to maintain order
        tup = unordered_patient_medication_alert[alert.patient]
        lst = list(tup)
        lst.append((medication, alert))
        unordered_patient_medication_alert[alert.patient] = tuple(lst)

    # Sort patients by full_name
    medication_patients = unordered_patient_medication_alert.keys()
    medication_patients.sort(key=lambda x: x.full_name)

    for patient in medication_patients:
        ordered_patient_medication_alert.append((patient, unordered_patient_medication_alert[patient]))
    

    following_patients = request.user.doctor.patients.all()

    context = {
        "title":_("Dashboard"),
        "year":datetime.datetime.now().year,
        "unread_patients": unread_patients,
        "patient_esas_alert": ordered_patient_esas_alert,
        "patient_medication_alert": ordered_patient_medication_alert,
        "following_patients": following_patients,
    }


    return render(
        request,
        "app/dashboard.html",
        context
    )


def login_redirect(request, **kwargs):
    # Checks to see if user is logged in. If so, redirect to dashboard page.
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("dashboard"))
    else:
        return auth_views.login(request, **kwargs)

def patients(request):
    """Renders the patients page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("login"))

    print "request.user.username:", request.user.username

    patient_results = []

    if request.method == "GET":
        print "[views.searchPatients] got GET request"

        # Get "patient_query" url param
        patient_query = request.GET.get("patient_query", "")
        print "patient_query:", patient_query

        doctor = Doctor.objects.get(user=request.user)
        print "doctor:", doctor

        if patient_query == "":
            # No specific patient query. Show all patients
            #patient_results = doctor.patients.all()
            patient_results = Patient.objects.all()

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
        "title": _("Patients"),
        "message": _("List of patients."),
        "year": datetime.datetime.now().year,
        "patient_results": patient_results,
        "query_patients_form": query_patients_form,
    }

    return render(
        request,
        "app/patients.html",
        context
    )

def follow_patient(request):
    """ Handle a doctor following a patient """

    doctor = Doctor.objects.get(pk=request.POST["doctor_pk"])
    patient = Patient.objects.get(pk=request.POST["patient_pk"])

    doctor.patients.add(patient)

    return HttpResponseRedirect("/patients")

def unfollow_patient(request):
    """ Handle a doctor unfollowing a patient """

    doctor = Doctor.objects.get(pk=request.POST["doctor_pk"])
    patient = Patient.objects.get(pk=request.POST["patient_pk"])

    doctor.patients.remove(patient)

    return HttpResponseRedirect("/patients")


def patient_profile(request):
    """Renders the patient profile page."""
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("login"))

    print request.GET

    patient_pk = request.GET["pk"]
    print "patient_pk:", patient_pk  

    patient_obj = Patient.objects.get(pk=patient_pk)

    notes_form = PatientNotesForm(initial={"notes": patient_obj.doctor_notes})
    create_notification_form = CreateNotificationForm()
    add_video_form = AddVideoForm()
    create_medication_form = CreateMedicationForm()
    upload_image_form = UploadImageForm()
    edit_patient_form = EditPatientForm()

    edit_patient_form.fields["pk"].initial = patient_obj.pk
    ### Home tab.
    editing_patient = False
    if "edit" in request.GET:
        print "edit:", request.GET["edit"]
        editing_patient = True

        edit_patient_form.fields["full_name"].initial = patient_obj.full_name
        edit_patient_form.fields["hospital_id"].initial = patient_obj.hospital_id
        edit_patient_form.fields["esas_alert"].initial = patient_obj.esas_alert
        edit_patient_form.fields["age"].initial = patient_obj.age
        edit_patient_form.fields["gender"].initial = patient_obj.gender
        edit_patient_form.fields["treatment_type"].initial = patient_obj.treatment_type
        edit_patient_form.fields["tumor_type"].initial = patient_obj.tumor_type
        edit_patient_form.fields["comorbidities"].initial = patient_obj.comorbidities
        edit_patient_form.fields["caregiver_name"].initial = patient_obj.caregiver_name
        edit_patient_form.fields["caregiver_relationships"].initial = patient_obj.caregiver_relationships
        edit_patient_form.fields["city_of_residence"].initial = patient_obj.city_of_residence
        edit_patient_form.fields["telephone"].initial = patient_obj.telephone
        edit_patient_form.fields["next_appointment"].initial = patient_obj.next_appointment

        print "edit_patient_form:", edit_patient_form.fields

    ### Notifications tab.
    notifications = Notification.objects.filter(patient=patient_obj)

    #### Videos tab.
    videos = Video.objects.filter(patient=patient_obj)

    ### Messages tab.
    channels = []
    channels.append(get_channel(request, patient_obj))
    token = get_token(request.user.username)
    """
    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        if c.unique_name == patient_obj.user.username:
            print "selected channel", c.friendly_name, c.sid
            channel_json = {
                "sid": str(c.sid),
                "unique_name": str(c.unique_name),
                "friendly_name": str(c.friendly_name),
            }
            channels.append(channel_json)
            break

    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, request.user.username)
    endpoint = "PalliAssist:" + request.user.username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)
    """

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

    pain_images = PainImages.objects.filter(patient=patient_obj)


    ### Medication tab.
    medications = Medication.objects.filter(patient=patient_obj)
    for med in medications:
        med.posology = "h, ".join(med.posology.split(";")) + "h"

    medication_reports = MedicationReport.objects.filter(patient=patient_obj)

    context = {
        "title": _("Patient Profile"),
        "message": _("Patient profile."),
        "year": datetime.datetime.now().year,
        "patient": patient_obj,
        "editing_patient": editing_patient,
        "edit_patient_form": edit_patient_form,
        "notes_form": notes_form,
        "add_video_form": add_video_form,
        "create_notification_form": create_notification_form,
        "create_medication_form": create_medication_form,
        "upload_image_form": upload_image_form,
        "notifications": notifications,
        "videos": videos,
        "medications": medications,
        "medication_reports": medication_reports,
        "esas_objects": esas_objects,
        "esas_json": esas_json,
        "pain_objects": pain_objects,
        "pain_width": 207,
        "pain_height": 400,
        "pain_images": pain_images,
        "channels": channels, 
        "token": token, # Twilio token for messaging tab.
    }

    return render(
        request,
        "app/patient_profile.html",
        context
    )

def edit_patient_info(request):
    print "edit_patient_info request:", request.POST

    edit_patient_form = EditPatientForm(request.POST)
    return HttpResponseRedirect("/patient-profile?pk=" + str(edit_patient_form.data["pk"]) + "&edit=true")


def save_patient_info(request):
    """ """
    print "save_patient_info request:", request.POST
    edit_patient_form = EditPatientForm(request.POST)

    if edit_patient_form.is_valid():
        form_data = edit_patient_form.cleaned_data
        patient = Patient.objects.get(pk=form_data["pk"])

        if form_data["hospital_id"]:
            patient.hospital_id = form_data["hospital_id"]
        if form_data["full_name"]:
            patient.full_name = form_data["full_name"]
        if form_data["age"]:
            patient.age = form_data["age"]
        if form_data["gender"]:
            patient.gender = form_data["gender"]
        if form_data["telephone"]:
            patient.telephone = form_data["telephone"]
        if form_data["esas_alert"]:
            patient.esas_alert = form_data["esas_alert"]
        if form_data["city_of_residence"]:
            patient.city_of_residence = form_data["city_of_residence"]
        if form_data["caregiver_name"]:
            patient.caregiver_name = form_data["caregiver_name"]
        if form_data["caregiver_relationships"]:
            patient.caregiver_relationships = form_data["caregiver_relationships"]
        if form_data["treatment_type"]:
            patient.treatment_type = form_data["treatment_type"]
        if form_data["tumor_type"]:
            patient.tumor_type = form_data["tumor_type"]
        if form_data["comorbidities"]:
            patient.comorbidities = form_data["comorbidities"]
        if form_data["next_appointment"]:
            patient.next_appointment = form_data["next_appointment"]

        patient.save()

        return HttpResponseRedirect("/patient-profile?pk=" + str(patient.pk))

    return HttpResponseRedirect("/patient-profile?pk=" + str(edit_patient_form.data["pk"]) + "&edit=true")


def patient_signup(request):

    if request.method == "POST":
        patient_signup_form = PatientSignupForm(request.POST, error_class=DivErrorList)
        doctor_signup_form = SignupForm(error_class=DivErrorList)

        if patient_signup_form.is_valid():
            username = patient_signup_form.cleaned_data["username"]
            password = patient_signup_form.cleaned_data["password_1"]
            #role = signup_form.cleaned_data["doctor_patient_choice"]

            user = User.objects.create_user(username=username, password=password)

            print patient_signup_form.cleaned_data

            # Create User and Patient object.
            patients_doctor_username = patient_signup_form.cleaned_data["patients_doctor_username"]
            patient = Patient.objects.create(
                    user=user, 
                    full_name=patient_signup_form.cleaned_data["full_name"],
                    telephone=patient_signup_form.cleaned_data["telephone"],
                    age=patient_signup_form.cleaned_data["age"],
                    city_of_residence=patient_signup_form.cleaned_data["city_of_residence"],
                    caregiver_name=patient_signup_form.cleaned_data["caregiver_name"],
                    caregiver_relationships=patient_signup_form.cleaned_data["caregiver_relationships"],
                    treatment_type=patient_signup_form.cleaned_data["treatment_type"],
                    tumor_type=patient_signup_form.cleaned_data["tumor_type"],
                    comorbidities=patient_signup_form.cleaned_data["comorbidities"],
                    gender=patient_signup_form.cleaned_data["gender"]
            )
            Doctor.objects.get(user=User.objects.get(username=patients_doctor_username)).patients.add(patient)

            return HttpResponseRedirect("/signup-success/")

    context = {
        "title": _("Sign Up"),
        "year": datetime.datetime.now().year,
        "active_form": "patient",
        "patient_signup_form": patient_signup_form,
        "doctor_signup_form": doctor_signup_form,
    }

    return render(
        request,
        "app/sign_up.html",
        context
    )

def doctor_signup(request):

    if request.method == "POST":
        patient_signup_form = PatientSignupForm(error_class=DivErrorList)
        doctor_signup_form = SignupForm(request.POST, error_class=DivErrorList)

        if doctor_signup_form.is_valid():
            full_name = doctor_signup_form.cleaned_data["full_name"]
            username = doctor_signup_form.cleaned_data["username"]
            telephone = doctor_signup_form.cleaned_data["telephone"]
            password = doctor_signup_form.cleaned_data["password_1"]
            #role = signup_form.cleaned_data["doctor_patient_choice"]

            user = User.objects.create_user(username=username, password=password)

            # Create User and Doctor object.
            doctor = Doctor.objects.create(user=user, full_name=full_name, telephone=telephone)

            return HttpResponseRedirect("/signup-success/")

    context = {
        "title": _("Sign Up"),
        "year": datetime.datetime.now().year,
        "active_form": "doctor",
        "patient_signup_form": patient_signup_form,
        "doctor_signup_form": doctor_signup_form,
    }

    return render(
        request,
        "app/sign_up.html",
        context
    )


def signup(request):
    """Renders the patients page."""
    assert isinstance(request, HttpRequest)

    patient_signup_form = PatientSignupForm(error_class=DivErrorList)
    doctor_signup_form = SignupForm(error_class=DivErrorList)

    context = {
        "title": _("Sign Up"),
        "year": datetime.datetime.now().year,
        "active_form": "doctor",
        "patient_signup_form": patient_signup_form,
        "doctor_signup_form": doctor_signup_form,
    }

    return render(
        request,
        "app/sign_up.html",
        context
    )

def signup_success(request):
    """Renders the page after a user has successfully signed up."""
    assert isinstance(request, HttpRequest)


    context = {
        "title": _("Sign Up"),
        "year": datetime.datetime.now().year,
    }

    return render(
        request,
        "app/sign_up_success.html",
        context
    )


def messages(request):
    """ Renders the messages page. """
    assert isinstance(request, HttpRequest)

    # Check if user is logged in. Otherwise redirect to login page.
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse("login"))

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
        "sid": str(demo_channel.sid),
        "unique_name": str(demo_channel.unique_name),
        "friendly_name": str(demo_channel.friendly_name),
    }
    #demo_channel.update(unique_name="demochannel")
    member = demo_channel.members.create(identity=request.user.username)

    """
    channels = []
    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        print "looking at", c.friendly_name, c.unique_name, c.sid
        for m in c.members.list():
            print "identity", m.identity
            # Assuming that all twilio identities are based off of usernames
            if m.identity == request.user.username:
                # str() needed to get rid of u"hello" when escaping the string to javascript.
                print "selected channel", c.friendly_name, c.unique_name, c.sid
                channel_json = {
                    "sid": str(c.sid),
                    "unique_name": str(c.unique_name),
                    "friendly_name": str(c.friendly_name),
                }
                channels.append(channel_json)
                break

        print "== Channel =="
        print "\tsid: ", c.sid
        print "\tunique_name: ", c.unique_name
        print "\tfriendly_name: ", c.friendly_name
        print "\tattributes: ", c.attributes
        print "\tlinks: ", c.links
        print "\tmembers:"
        for m in c.members.list():
            print "\t\t", m.identity
    
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, request.user.username)
    endpoint = "PalliAssist:" + request.user.username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)
    """

    channels = []
    for p in Patient.objects.all():
        channels.append(get_channel(request, p))

    token = get_token(request.user.username)
    upload_image_form = UploadImageForm()

    patients = Patient.objects.all()

    context = {
        "title": _("Messages"),
        "message": _("Send messages."),
        "upload_image_form": upload_image_form,
        "year":datetime.datetime.now().year,
        "patients": patients,
        "channels": channels,
        "token": token,
    }

    return render(
        request,
        "app/messages.html",
        context
    )

def get_channel(request, patient):
    """ 
    Get list of twilio channels that the patient is a part of. If the patient
    doesn't have a channel yet, create one for it. Always create the 
    request.user (should be the doctor) as a member in case he hasn't been 
    added as a member yet.
    """
    channel_json = {}

    # List the channels that the user is a member of
    for c in settings.TWILIO_IPM_SERVICE.channels.list():
        if c.unique_name == patient.user.username:
            print "selected channel", c.friendly_name, c.sid
            if request != None:
                c.members.create(identity=request.user.username)
            channel_json = {
                "sid": str(c.sid),
                "unique_name": str(c.unique_name),
                "friendly_name": str(c.friendly_name),
            }
            break

    if channel_json == {}:
        # We didn't find a channel. Create one
        new_channel = settings.TWILIO_IPM_SERVICE.channels.create(unique_name=patient.user.username, friendly_name=patient.full_name, type="private")
        if request != None:
            new_channel.members.create(identity=request.user.username)
        new_channel.members.create(identity=patient.user.username)
        new_channel.members.create(identity=patient.full_name)
        channel_json = {
            "sid": str(new_channel.sid),
            "unique_name": str(new_channel.unique_name),
            "friendly_name": str(new_channel.friendly_name),
        }


    return channel_json

def get_token(username):

    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, username)
    endpoint = "PalliAssist:" + username + ":web"
    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    return token


def token(request):
    """
    Gets an access token for Twilio IP messaging. Called by messages.js.
    """
    assert isinstance(request, HttpRequest)

    # create a randomly generated username for the client
    identity = request.GET["identity"]

    # <unique app>:<user>:<device>
    endpoint = "PalliAssist:" + identity + ":mobile"

    # Create access token with credentials
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, identity)

    # Create an IP Messaging grant and add to token
    ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
    token.add_grant(ipm_grant)

    # COMMENTED CAUSE FLASK THING - Return token info as JSON
    #return jsonify(identity=identity, token=token.to_jwt())
    return JsonResponse({"identity": identity, "token": token.to_jwt()})
    #return JsonResponse({"identity": identity, "token": token})

def save_notes(request):
    """
    Saves notes about patients. POST request from 
    PatientNotesForm on the patient profile page. 
    jQuery runs when save button is clicked.
    """
    assert isinstance(request, HttpRequest)

    print request.POST
    doctor_notes = request.POST["notes"]
    print "doctor_notes:", doctor_notes
    patient_pk = request.POST["pk"]

    patient = Patient.objects.get(pk=patient_pk)
    patient.doctor_notes = doctor_notes
    patient.save()

    return JsonResponse({})

@csrf_exempt
def delete_notification(request):
    """
    Creates a Notification model based on uer input.
    """
    print request.POST

    # Notification's PK
    Notification.objects.get(pk=int(request.POST["pk"])).delete()

    return JsonResponse({})

def create_notification(request):
    """
    Creates a Notification model based on uer input.
    """

    # Patient's PK
    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    Notification.objects.create(
            created_date=timezone.now(), 
            category=request.POST["category"], 
            text=request.POST["text"], 
            patient=patient_obj
    )

    return JsonResponse({})

def add_video(request):
    """
    Creates a Video model based on url.
    """

    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    # Delete all current videos associated with this patient. 
    # So there's only one video per patient.
    Video.objects.filter(patient=patient_obj).delete()

    video = Video.objects.create(
            patient=patient_obj,
            url=request.POST["url"]
    )

    data_message = {
        "event": "NOTIFICATION",
        "action": "CREATE",
        "category": "VIDEO",
        "data": {
            "videos": serializers.serialize("json", [video])
        }
    }
    #sendFCM(data_message, "test")
    sendFCM(data_message, patient_obj.user.username)

    print request
    print video
    return JsonResponse({})

@csrf_exempt
def delete_video(request):
    """
    Creates a Video model based on url.
    """

    Video.objects.get(pk=int(request.POST["pk"])).delete()

    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    data_message = {
        "event": "NOTIFICATION",
        "action": "DELETE",
        "category": "VIDEO",
        "pk": request.POST["pk"]
    }
    #sendFCM(data_message, "test")
    sendFCM(data_message, patient_obj.user.username)

    return JsonResponse({})


@csrf_exempt
def delete_medication(request):
    """
    Deletes a medication object for a patient.
    """
    print "delete_medication"
    print request.POST

    patient_obj = Patient.objects.get(pk=int(request.POST["patient_pk"]))

    # Notification's PK
    Medication.objects.get(pk=int(request.POST["medication_pk"])).delete()

    data_message = {
        "event": "NOTIFICATION",
        "action": "DELETE",
        "category": "MEDICATION",
        "pk": request.POST["medication_pk"]
    }
    #sendFCM(data_message, "test")
    sendFCM(data_message, patient_obj.user.username)

    return HttpResponseRedirect("/patient-profile?pk=" + str(request.POST["patient_pk"] + "#medications"))

def create_medication(request):
    """
    Creates a Medication model based on user input.
    """
    print
    print "create_medication"
    patient_obj = Patient.objects.get(pk=request.POST["pk"])

    medication = Medication.objects.create(
            created_date=timezone.now(),
            patient=patient_obj,
            name=request.POST["name"],
            form=request.POST["form"],
            dose=request.POST["dose"],
            num_doses=request.POST["num_doses"],
            dose_time_1=request.POST["dose_time_1"],
            dose_time_2=request.POST["dose_time_2"],
            dose_time_3=request.POST["dose_time_3"],
            dose_time_4=request.POST["dose_time_4"],
            dose_time_5=request.POST["dose_time_5"],
            dose_time_6=request.POST["dose_time_6"],
            rescue=request.POST["rescue"]
    )

    print Medication.objects.get(pk=medication.pk)
    print serializers.serialize("json", Medication.objects.filter(pk=medication.pk))

    data_message = {
        "event": "NOTIFICATION",
        "action": "CREATE",
        "category": "MEDICATION",
        "data": {
            "medications": serializers.serialize("json", Medication.objects.filter(pk=medication.pk))
        }
    }
    #sendFCM(data_message, "test")
    sendFCM(data_message, patient_obj.user.username)

    print CreateMedicationForm(request.POST)
    print request
    print

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
        blob_name = patient_obj.user.username + "_" + str(convert_datetime_to_millis(datetime.datetime.now()))

        settings.BLOCK_BLOB_SERVICE.create_container(container_name, public_access=PublicAccess.Container)
        settings.BLOCK_BLOB_SERVICE.create_blob_from_path(container_name, blob_name, image_obj.image.path, content_settings=ContentSettings(content_type="image/png"))
        success = True

    else:
        message = _("Error uploading image. Please try again.")


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

    print request.POST["channel_name"]
    channel_name = request.POST["channel_name"]

    new_channel = settings.TWILIO_IPM_SERVICE.channels.create(friendly_name=channel_name, type="private")
    new_channel.members.create(identity=request.user.username)

    print new_channel
    print new_channel.type
    print new_channel.friendly_name
    print new_channel.unique_name

    return JsonResponse({})

def check_esas_alert(patient, esas):
    """
    Checks to see if we need to create a dashboard alert for
    this esas. If a symptom intensity has exceeded the custom 
    esas alert for the patient.
    """

    limit = patient.esas_alert

    if esas.pain >= limit:
        return True
    elif esas.fatigue >= limit:
        return True
    elif esas.nausea >= limit:
        return True
    elif esas.depression >= limit:
        return True
    elif esas.anxiety >= limit:
        return True
    elif esas.drowsiness >= limit:
        return True
    elif esas.appetite >= limit:
        return True
    elif esas.well_being >= limit:
        return True
    elif esas.lack_of_air >= limit:
        return True
    elif esas.insomnia >= limit:
        return True

    return False


def handle_completed_esas(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a ESAS survey.
    """

    print "handle_completed_esas"
    print data
    print type(data)
    print data["pain"]
    print int(data["pain"])

    esas = ESASSurvey.objects.create(created_date=dt, patient=patient_obj)
    esas.pain = int(data["pain"])
    print "pain", esas.pain
    esas.fatigue = int(data["fatigue"])
    esas.nausea = int(data["nausea"])
    esas.depression = int(data["depression"])
    esas.anxiety = int(data["anxiety"])
    esas.drowsiness = int(data["drowsiness"])
    esas.appetite = int(data["appetite"])
    esas.well_being = int(data["well_being"])
    esas.lack_of_air = int(data["lack_of_air"])
    esas.insomnia = int(data["insomnia"])

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

    if check_esas_alert(patient_obj, esas):
        DashboardAlert.objects.create(category=DashboardAlert.ESAS, patient=patient_obj, item_pk=esas.pk)

def handle_completed_medication(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a medication.
    """

    print data
    report = MedicationReport.objects.create(created_date=dt, patient=patient_obj)
    alert = False

    for entry in data:
        print "entry", entry
        medication = Medication.objects.get(pk=entry["pk"])
        report_entry = MedicationReportEntry.objects.create(medication=medication)

        entry["statuses"] = json.loads(entry["statuses"])
        for status in entry["statuses"]:
            print status
            print type(status)
            if status["completed"] == "yes":
                med_status =  MedicationStatus.objects.create(time=status["time"], completed=True)
            else:
                # Make dashboard alert
                alert = True
                med_status = MedicationStatus.objects.create(time=status["time"], completed=False)

            report_entry.statuses.add(med_status)
            
        report.entries.add(report_entry) 

    if alert:
        DashboardAlert.objects.create(category=DashboardAlert.MEDICATION, patient=patient_obj, item_pk=report.pk)


    print medication
    print medication.patient

def handle_completed_pain(dt, patient_obj, data):
    """
    Handler for receiving a POST request form mobile, indicating 
    that a patient has completed a pain survey.
    """
    print "handle_completed_pain"
    pain_image = PainImages.objects.create(
            patient=patient_obj, 
            created_date=dt, 
            container_name = data["container_name"], 
            front_blob_name=data["front_blob_name"], 
            back_blob_name=data["back_blob_name"],
            left_blob_name=data["left_blob_name"],
            right_blob_name=data["right_blob_name"],
        )
    print pain_image


def handle_mobile_login(data, topic):
    print "handle_mobile_login"
    print "username", data["username"]
    print "password", data["password"]

    user = authenticate(username=data["username"], password=data["password"])
    print user
    if user != None:
        print serializers.serialize("json", [user.patient])

    if user is not None:
        patient_obj = user.patient

        # TODO. make this the same format as handle_patient_registration
        # event: LOGIN
        # action: SUCCESS/ERROR
        # category: etc.

        data_message = {
            "event": "LOGIN",
            "action": "SUCCESS",
            "category": "AUTHORIZATION",
            "data": {
                "success": "yes",
                "patient": serializers.serialize("json", [patient_obj]),
                "videos": serializers.serialize("json", Video.objects.filter(patient=patient_obj)),
                "medications": serializers.serialize("json", Medication.objects.filter(patient=patient_obj)),
                "channel_sid": get_channel(None, patient_obj)["sid"]
            }
        }
    else:
        data_message = {
            "event": "LOGIN",
            "action": "ERROR",
            "category": "AUTHORIZATION",
            "data": {
                "success": "no",
            }
        }

    sendFCM(data_message, topic)

def check_access_key(data):
    # Check if valid access key. Reading from access_keys.txt from project root.
    access_keys_file = open(os.path.join(settings.PROJECT_ROOT, "access_keys.txt"))
    access_keys_list = access_keys_file.read().splitlines()

    if data["access_key"] not in access_keys_list:
        return False
    return True

def handle_patient_registration(data, topic):
    """ Register a patient from the mobile side """

    print "handle_patient_registration"

    
    try:
        patient_user = User.objects.get(username=data["patient_username"])

        # TODO: send fcm of error: patient username already exists
        print "send fcm of error: patient username already exists"
        data_message = {
            "event": "REGISTRATION",
            "action": "ERROR",
            "category": "PATIENT",
            "data": {
                "error": "Username already taken. Please try a different one."
            }
        }
        sendFCM(data_message, topic)
    except User.DoesNotExist:
        # patient username does not exist. this is to be expected

        try:
            doctor_user = User.objects.get(username=data["doctor_username"])

            doctor = Doctor.objects.get(user=doctor_user)

            # Checking for valid access key
            valid_access_key = check_access_key(data)

            if not valid_access_key:
                # TODO: send fcm of error; invalid access key
                print "send fcm of error: invalid access key"
                data_message = {
                    "event": "REGISTRATION",
                    "action": "ERROR",
                    "category": "PATIENT",
                    "data": {
                        "error": "Invalid access key."
                    }
                }
                sendFCM(data_message, topic)

            # Creating patient User object.
            patient_user = User.objects.create_user(username=data["patient_username"], password=data["password"])

            # Create Patient object
            patient = Patient.objects.create(
                    user=patient_user,
                    full_name=data["full_name"],
                    telephone=data["telephone"],
                    age=data["age"],
                    city_of_residence=data["city_of_residence"],
                    caregiver_name=data["caregiver_name"],
                    treatment_type=data["treatment_type"],
                    gender=data["gender"],
                    tumor_type=data["tumor_type"],
                    comorbidities=data["comorbidities"],
                    caregiver_relationships=data["caregiver_relationships"],
            )

            # Add patient to that doctor's list of patients
            doctor.patients.add(patient)

            print "new patient:", patient
            print "new patient_user:", patient_user
            print "referenced doctor:", doctor 

            data_message = {
                "event": "REGISTRATION",
                "action": "SUCCESS",
                "category": "PATIENT",
                "data": { }
            }
            sendFCM(data_message, topic)
            """
                "patient": serializers.serialize("json", [patient]),
                "videos": serializers.serialize("json", Video.objects.filter(patient=patient)),
                "medications": serializers.serialize("json", Medication.objects.filter(patient=patient)),
            """



        except User.DoesNotExist:
            # Doctor user does not exist

            # TODO: send fcm of error: doctor username does not exist
            print "send fcm of error: doctor username does not exist"
            data_message = {
                "event": "REGISTRATION",
                "action": "ERROR",
                "category": "PATIENT",
                "data": {
                    "error": "Doctor username not found."
                }
            }
            sendFCM(data_message, topic)





@csrf_exempt
def mobile(request):
    """
    Handle FCM requests from mobile.
    Format described in Meeting Minutes Feb 2, 2017
    """
    assert isinstance(request, HttpRequest)

    print request.POST

    event = request.POST["event"]

    if event == "TESTING":
        return JsonResponse({"hello": "world"})

    if event == "COMPLETED":
        patient_username = request.POST["patient"] # TODO hardcoded to patient0 right now 
        patient_obj = User.objects.get(username=patient_username).patient
        print "patient_obj", patient_obj 

        timestamp = request.POST["timestamp"] # milliseconds
        dt_unaware = datetime.datetime.fromtimestamp(int(timestamp)/1000.0)
        dt_aware = timezone.make_aware(dt_unaware, timezone.get_current_timezone())
        print "dt_aware", dt_aware 

        if request.POST["category"] == "MEDICATION":
            handle_completed_medication(dt_aware, patient_obj, json.loads(request.POST["data"]))
            return JsonResponse({})

        elif request.POST["category"] == "PAIN":
            handle_completed_pain(dt_aware, patient_obj, json.loads(request.POST["data"]))
            return JsonResponse({})

        elif request.POST["category"] == "ESAS":
            handle_completed_esas(dt_aware, patient_obj, json.loads(request.POST["data"]))
            return JsonResponse({})

    elif event == "LOGIN":
        if request.POST["category"] == "AUTHORIZATION":
            handle_mobile_login(json.loads(request.POST["data"]), request.POST["topic"])
            return JsonResponse({})


    elif event == "REGISTRATION":
        if request.POST["category"] == "PATIENT":
            print "post: REGISTRATION, PATIENT"
            handle_patient_registration(json.loads(request.POST["data"]), request.POST["topic"])
            return JsonResponse({})
        

    # TODO. return an error.

    return render(request, "app/blank.html")

def sendFCM(data_message, topic):
    print 
    print "sending fcm:"
    print data_message
    print
    result = settings.FCM_SERVICE.notify_topic_subscribers(topic_name=topic, data_message=data_message)


@csrf_exempt
def set_language(request):
    """ 
    Set language of website.
    """
    print "set_language"
    language = request.POST["language"]
    print "language:", language
    translation.activate(language)
    print "get_language:", translation.get_language()
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return HttpResponseRedirect(request.POST["next"]) 
    


@csrf_exempt
def sync_redcap(request):
    """ 
    Syncs all django models with the REDCap records.
    django primary_key in model == REDCap record_id in record.
    """

    URL = "https://hcbredcap.com.br/api/"
    #USER_TOKEN = "F2C5AEE8A2594B0A9E442EE91C56CC7A"
    MEDICATION_TOKEN = "2D58F93CB3B9C8C2FD00E64BD12080A3"
    ESAS_TOKEN = "7048C161E7BE6A8B86F5100D5FDA7C20"
    PAIN_TOKEN = "B91EDA097393C04D5F2C1526E1F7CD37"
    PATIENT_TOKEN = "A1E9884F5A90E5270385D131B66659CE"
    DOCTOR_TOKEN = "8400B14C28F7E6C644E0ADB5AE5F4628"

    #REDCAP_USER_PROJECT = Project(URL, USER_TOKEN)
    REDCAP_MEDICATION_PROJECT = Project(URL, MEDICATION_TOKEN)
    REDCAP_ESAS_PROJECT = Project(URL, ESAS_TOKEN)
    REDCAP_PAIN_PROJECT = Project(URL, PAIN_TOKEN)
    REDCAP_PATIENT_PROJECT = Project(URL, PATIENT_TOKEN)
    REDCAP_DOCTOR_PROJECT = Project(URL, DOCTOR_TOKEN)

    # Medications 
    medications = Medication.objects.all()
    
    medication_data = []
    for medication in medications:
        medication_data.append({
            "record_id": medication.pk,
            "created_date": formatRedcapDate(medication.created_date),
            "name": medication.name,
            "form": medication.form,
            "dose": medication.dose,
            "posology": medication.posology,
            "rescue": medication.rescue
        })


    medication_response = REDCAP_MEDICATION_PROJECT.import_records(medication_data, overwrite="overwrite")
    print "medication models:", len(medications)
    print "medication_response:", medication_response["count"]

    # ESAS 
    esas_surveys = ESASSurvey.objects.all()
    esas_data = []
    for esas_survey in esas_surveys:
        esas_data.append({
            "record_id": esas_survey.pk,
            "created_date": formatRedcapDate(esas_survey.created_date),
            "patient": esas_survey.patient.pk,
            "pain": esas_survey.pain,
            "fatigue": esas_survey.fatigue,
            "nausea": esas_survey.nausea,
            "depression": esas_survey.depression,
            "anxiety": esas_survey.anxiety,
            "drowsiness": esas_survey.drowsiness,
            "appetite": esas_survey.appetite,
            "well_being": esas_survey.well_being,
            "lack_of_air": esas_survey.lack_of_air,
            "insomnia": esas_survey.insomnia,
            "fever": esas_survey.fever,
            "constipated": esas_survey.constipated,
            "constipated_days": esas_survey.constipated_days,
            "constipated_bothered": esas_survey.constipated_bothered,
            "vomiting": esas_survey.vomiting,
            "vomiting_count": esas_survey.vomiting_count,
            "confused": esas_survey.confused
        })
    esas_response = REDCAP_ESAS_PROJECT.import_records(esas_data, overwrite="overwrite")

    print "esas models:", len(esas_surveys)
    print "esas_response:", esas_response["count"]

    # PAIN
    pain_images = PainImages.objects.all()
    pain_data = []
    for pain_image in pain_images:
        pain_data.append({
            "record_id": pain_image.pk,
            "created_date": formatRedcapDate(pain_image.created_date),
            "patient": pain_image.patient.pk,
            "container_name": pain_image.container_name,
            "front_blob_name": pain_image.front_blob_name,
            "back_blob_name": pain_image.back_blob_name,
            "left_blob_name": pain_image.left_blob_name,
            "right_blob_name": pain_image.right_blob_name,
        })
    pain_response = REDCAP_PAIN_PROJECT.import_records(pain_data, overwrite="overwrite")

    print "pain models:", len(pain_images)
    print "pain_response:", pain_response["count"]

    # Doctor 
    doctors = Doctor.objects.all()
    doctor_data = []
    for doctor in doctors:
        doctor_data.append({
            "record_id": doctor.pk,
            "username": doctor.user.username,
            "full_name": doctor.full_name,
            "telephone": doctor.telephone
        })
    doctor_response = REDCAP_DOCTOR_PROJECT.import_records(doctor_data, overwrite="overwrite")

    print "doctor models:", len(doctors)
    print "doctor_response:", doctor_response["count"]

    # Patient 
    patients = Patient.objects.all()
    patient_data = []
    for patient in patients:
        patient_data.append({
            "record_id": patient.pk,
            "hospital_id": patient.hospital_id,
            "username": patient.user.username,
            "full_name": patient.full_name,
            "telephone": patient.telephone,
            "age": patient.age,
            "gender": patient.gender,
            "city_of_residence": patient.city_of_residence,
            "caregiver_name": patient.caregiver_name,
            "treatment_type": patient.treatment_type,
            "esas_alert": patient.esas_alert,
        })
        """
        # TODO: add fields to patient_data after adding to redcap models
        "tumor_type": patient.tumor_type,
        "comorbidities": patient.comorbidities,
        "caregiver_relationships": patient.caregiver_relationships,
        """

    patient_response = REDCAP_PATIENT_PROJECT.import_records(patient_data, overwrite="overwrite")

    print "patient models:", len(patients)
    print "patient_response:", patient_response["count"]


    return JsonResponse({})

def twoDigit(num):
    """ Will return a string representation of the num with 2 digits. e.g. 6 => 06 """
    if num < 10:
        return "0" + str(num)
    return str(num)

def formatRedcapDate(dt):
    """ Formats datetime into D-M-Y H:M """

    month = twoDigit(dt.month)
    day = twoDigit(dt.day)
    hour = twoDigit(dt.hour)
    minute = twoDigit(dt.minute)

    return str(dt.year) + "-" + month + "-" + day + " " + hour + ":" + minute


@csrf_exempt
def delete_dashboard_alert(request):
    """
    Deletes a dashboard alert object for a patient.
    """
    print request.POST

    # Notification's PK
    DashboardAlert.objects.get(pk=int(request.POST["pk"])).delete()

    return JsonResponse({})


def convert_datetime_to_millis(dt):
    return (dt.replace(tzinfo=None) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000

def admin_input(request):

    return render(
        request,
        "app/admin_input.html",
        {}
    )

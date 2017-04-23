"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
from django.utils import timezone
from django.core import serializers
from django.contrib.auth import authenticate

from phonenumber_field.modelfields import PhoneNumberField

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient

import datetime
import os

# Create your models here.
MAX_LENGTH = 255

class Patient(models.Model):
    """
    Contains info on a patient.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=MAX_LENGTH)
    telephone = models.TextField(default="")
    age = models.IntegerField(default=0) 
    city_of_residence = models.TextField(default="")
    caregiver_name = models.CharField(max_length=MAX_LENGTH, default="")
    next_appointment = models.DateTimeField(default=timezone.now)
    hospital_id = models.IntegerField(default=-1)
    esas_alert = models.IntegerField(default=7)

    PALLIATIVE = "Palliative Care Only"
    ANTICANCER = "Undergoing Anticancer Therapy"
    TREATMENT_CHOICES = (
        (PALLIATIVE, PALLIATIVE),
        (ANTICANCER, ANTICANCER),
    )
    treatment_type = models.CharField(max_length=MAX_LENGTH, choices=TREATMENT_CHOICES, default=PALLIATIVE)

    FEMALE = "Female"
    MALE = "Male"
    GENDER_CHOICES = (
        (FEMALE, FEMALE),
        (MALE, MALE),
    )
    gender = models.CharField(max_length=MAX_LENGTH, choices=GENDER_CHOICES, default="")

    doctor_notes = models.TextField(default="")
    unread_messages = models.IntegerField(default=0)


    def __unicode__(self):
        return "[Patient] " + str(self.user.username)

    class Meta:
        ordering = ('user_id',)


class Doctor(models.Model):
    """
    Contains info on a doctor.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=MAX_LENGTH)
    telephone = models.TextField(default="")
    patients = models.ManyToManyField(Patient)
    twilio_token = models.TextField(default="")

    def __unicode__(self):
        return "[Doctor] " + str(self.user.username)

    class Meta:
        ordering = ('user_id',)

class ESASQuestion(models.Model):
    """ Represents one question and answer on the ESAS survey. """
    question = models.TextField(default="")
    answer = models.IntegerField(default=0)

    def __unicode__(self):
        return "[ESASQuestion] " + str(self.question) + ": " + str(self.answer)

class ESASSurvey(models.Model):
    """ Encapsulates one survey. """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    pain = models.IntegerField(null=True)
    fatigue = models.IntegerField(null=True)
    nausea = models.IntegerField(null=True)
    depression = models.IntegerField(null=True)
    anxiety = models.IntegerField(null=True)
    drowsiness = models.IntegerField(null=True)
    appetite = models.IntegerField(null=True)
    well_being = models.IntegerField(null=True)
    lack_of_air = models.IntegerField(null=True)
    insomnia = models.IntegerField(null=True)

    # Custom questions
    fever = models.CharField(default="no", max_length=MAX_LENGTH)

    constipated = models.CharField(default="no", max_length=MAX_LENGTH)
    constipated_days = models.IntegerField(default=0)
    constipated_bothered = models.IntegerField(default=0)

    vomiting = models.CharField(default="no", max_length=MAX_LENGTH)
    vomiting_count = models.IntegerField(default=0)

    confused = models.CharField(default="no", max_length=MAX_LENGTH)

    class Meta:
        ordering = ('-created_date',)

class PainPoint(models.Model):
    """ Represents one question and answer on the ESAS survey. """
    x = models.IntegerField()
    y = models.IntegerField()
    intensity = models.IntegerField()
    rgb = models.IntegerField() # Set later, when calculating rgb value when passing to view

class PainSurvey(models.Model):
    """ Encapsulates one survey. """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    width = models.IntegerField()
    height = models.IntegerField()
    front_points = models.ManyToManyField(PainPoint, related_name="front_points")
    back_points = models.ManyToManyField(PainPoint, related_name="back_points")

class PainImages(models.Model):
    """ Images that show a pain location """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    container_name = models.CharField(default="", max_length=MAX_LENGTH)
    front_blob_name = models.CharField(default="", max_length=MAX_LENGTH)
    back_blob_name = models.CharField(default="", max_length=MAX_LENGTH)

    class Meta:
        ordering = ('-created_date',)

class Medication(models.Model):
    """ Info for one medication prescription. """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_LENGTH, default="")
    form = models.CharField(max_length=MAX_LENGTH, default="")
    dose = models.CharField(max_length=MAX_LENGTH, default="")
    posology = models.CharField(max_length=MAX_LENGTH, default="")
    rescue = models.TextField(default="")

    class Meta:
        ordering = ('-created_date',)

class MedicationStatus(models.Model):
    """ Status if a medication has been completed at its time. """
    time = models.CharField(max_length=MAX_LENGTH, default="")
    completed = models.NullBooleanField()

    class Meta:
        ordering = ('time',)

class MedicationReportEntry(models.Model):
    """ A entry for one medication in the report """
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    statuses = models.ManyToManyField(MedicationStatus, related_name="statuses")

class MedicationReport(models.Model):
    """ Info for one submitted medication report. """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    entries = models.ManyToManyField(MedicationReportEntry, related_name="entries")

    class Meta:
        ordering = ('-created_date',)

class Notification(models.Model):
    """ A notification for a patient or doctor. """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    text = models.TextField(default="")

    # (actual value, human readable form)
    CATEGORY_CHOICES = (
        ("ESAS", "ESAS"),
        ("PAIN", "Pain"),
        ("MEDICATION", "Medication"),
        ("OTHER", "Other"),
    )
    category = models.CharField(max_length=MAX_LENGTH, choices=CATEGORY_CHOICES, default="OTHER")

    class Meta:
        ordering = ('-created_date',)

class Video(models.Model):
    """ YouTube video for patients to watch. """
    url = models.URLField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


def user_directory_path(instance, imagename):
    """ Should upload to MEDIA/uploads/username/imagename """
    return os.path.join("uploads", instance.patient.user.username, imagename)


class Image(models.Model):
    """ An uploaded image """
    created_date = models.DateTimeField(default=timezone.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)

    class Meta:
        ordering = ('-created_date',)

class DashboardAlert(models.Model):
    """
    Parent class of all possible dashboard alerts.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    item_pk = models.IntegerField(default=0) 

    MEDICATION = "MEDICATION"
    ESAS = "ESAS"
    CATEGORY_CHOICES = (
        (MEDICATION, MEDICATION),
        (ESAS, ESAS),
    )
    category = models.CharField(max_length=MAX_LENGTH, choices=CATEGORY_CHOICES, default=MEDICATION)


"""
@receiver(post_save, sender=User)
def update_redcap_user(sender, **kwargs):

    instance = kwargs['instance']

    current_records = settings.REDCAP_USER_PROJECT.export_records()

    found = False 
    last_record_id = 0
    for r in current_records:
        if r['username'] == instance.username:
            found = True
            updated_r = {'record_id': r['record_id'], 'username': instance.username, 'password': instance.password}
            #updated_r = {'record_id': r.record_id, 'password': instance.password}
            settings.REDCAP_USER_PROJECT.import_records([updated_r])
            break

        last_record_id = r['record_id']

    if not found:
        new_r = {'record_id': str(int(last_record_id) + 1), 'username': instance.username, 'password': instance.password}
        print "new_r", new_r
        settings.REDCAP_USER_PROJECT.import_records([new_r])

    #########
"""

"""
    if kwargs.get('created', False):
        # New user was created.
        print "[receiver - update_redcap_user]"
"""

@receiver(user_logged_in)
def generateTwilioAccessToken(sender, **kwargs):
    print "user_logged_in receiver"
    print sender
    print kwargs['request']
    user = kwargs['user']

    try:
        doctor = user.doctor;

        # create a randomly generated username for the client
        identity = user.username;

        # <unique app>:<user>:<device>
        endpoint = "PalliAssist:" + identity + ":web"

        # Create access token with credentials
        token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, identity)

        # Create an IP Messaging grant and add to token
        ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_IPM_SERVICE_SID)
        token.add_grant(ipm_grant)


        doctor.twilio_token = token
        doctor.save()

        print doctor.twilio_token

    except Doctor.DoesNotExist:
        print "error. not a doctor logging in?"


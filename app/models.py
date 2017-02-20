"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient

import datetime

# Create your models here.
MAX_LENGTH = 255

class DashboardAlert(models.Model):
    """
    Parent class of all possible dashboard alerts.
    """
    resolved = models.BooleanField(default=False)

    class Meta:
        abstract = True


"""
Contains info on dashboard alerts of unread messages.
class UnreadMessage(DashboardAlert):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, primary_key=True)
    num_unread = models.IntegerField()
"""

class Patient(models.Model):
    """
    Contains info on a patient.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    sid = models.IntegerField() #hospital_id
    full_name = models.CharField(max_length=MAX_LENGTH)
    telephone = PhoneNumberField(default="")
    age = models.IntegerField(default=0) 
    city_of_residence = models.TextField(default="")
    caregiver_name = models.CharField(max_length=MAX_LENGTH, default="")
    next_appointment = models.DateTimeField(default=datetime.datetime.now)

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
    sid = models.IntegerField()
    full_name = models.CharField(max_length=MAX_LENGTH)
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
    created_date = models.DateTimeField(default=datetime.datetime.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    #questions = models.ManyToManyField(ESASQuestion)
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

class PainSurvey(models.Model):
    """ Encapsulates one survey. """
    created_date = models.DateTimeField(default=datetime.datetime.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    width = models.IntegerField()
    height = models.IntegerField()
    points = models.ManyToManyField(PainPoint)

class Medication(models.Model):
    """ Info for one medication prescription. """
    created_date = models.DateTimeField(default=datetime.datetime.now)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_LENGTH, default="")
    form = models.CharField(max_length=MAX_LENGTH, default="")
    dose = models.CharField(max_length=MAX_LENGTH, default="")
    posology = models.CharField(max_length=MAX_LENGTH, default="")
    rescue = models.TextField(default="")




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



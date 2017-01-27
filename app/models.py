"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.conf import settings

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient

# Create your models here.
NAME_MAX_LENGTH = 100

"""
Parent class of all possible dashboard alerts.
"""
class DashboardAlert(models.Model):
    resolved = models.BooleanField(default=False)

    class Meta:
        abstract = True


"""
Contains info on dashboard alerts of unread messages.
class UnreadMessage(DashboardAlert):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, primary_key=True)
    num_unread = models.IntegerField()
"""

"""
Contains info on a patient.
"""
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    u_id = models.IntegerField()
    full_name = models.CharField(max_length=NAME_MAX_LENGTH)
    doctor_notes = models.TextField(default="")
    unread_messages = models.IntegerField(default=0)

    def __unicode__(self):
        return "[Patient] " + str(self.user.username)

    class Meta:
        ordering = ('user_id',)


"""
Contains info on a doctor.
"""
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    u_id = models.IntegerField()
    full_name = models.CharField(max_length=NAME_MAX_LENGTH)
    patients = models.ManyToManyField(Patient)
    twilio_token = models.TextField(default="")

    def __unicode__(self):
        return "[Doctor] " + str(self.user.username)

    class Meta:
        ordering = ('user_id',)


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
        ipm_grant = IpMessagingGrant(endpoint_id=endpoint, service_sid=settings.TWILIO_SERVICE_SID)
        token.add_grant(ipm_grant)


        doctor.twilio_token = token
        doctor.save()

        print doctor.twilio_token

    except Doctor.DoesNotExist:
        print "error. not a doctor logging in?"



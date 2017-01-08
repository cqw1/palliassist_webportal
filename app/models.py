"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

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
"""
class UnreadMessage(DashboardAlert):
    patient_id = models.IntegerField()
    patient_name = models.CharField(max_length=NAME_MAX_LENGTH)
    num_unread = models.IntegerField()

"""
Contains info on a patient.
"""
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    u_id = models.IntegerField()
    full_name = models.CharField(max_length=NAME_MAX_LENGTH)

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

    def __unicode__(self):
        return "[Doctor] " + str(self.user.username)

    class Meta:
        ordering = ('user_id',)


@receiver(post_save, sender=User)
def update_redcap_user(sender, **kwargs):
    if kwargs.get('created', False):
        # New user was created.
        print "[receiver - update_redcap_user]"



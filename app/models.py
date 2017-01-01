"""
Definition of models.
"""

from django.db import models

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
Class to manage all unread message notifications.
"""
class UnreadMessageManager(models.Manager):
    def create_unread_message(self, patient_id, patient_name, num_unread):
        unread_message = self.create(patient_id=patient_id, patient_name=patient_name, num_unread=num_unread)

        # do something with the unread_message

        return unread_message


"""
Contains info on dashboard alerts of unread messages.
"""
class UnreadMessage(DashboardAlert):
    objects = UnreadMessageManager()

    patient_id = models.IntegerField()
    patient_name = models.CharField(max_length=NAME_MAX_LENGTH)
    num_unread = models.IntegerField()



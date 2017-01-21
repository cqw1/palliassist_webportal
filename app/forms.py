"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings 

from django.contrib.auth.models import User
from app.models import Doctor

import os

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Username'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class QueryPatientsForm(forms.Form):
    """ Queries for patients by name"""
    patient_query = forms.CharField(label=_("Search"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Search for patient'})) 

class PatientNotesForm(forms.Form):
    """ Queries for patients by name"""
    notes = forms.CharField(widget=forms.Textarea({ 'class': 'form-control', 'placeholder':'Add notes here.'}), label='') 

class SignupForm(forms.Form):
    """ Registering new users, both doctors and patients. """

    full_name = forms.CharField(label=_("Full Name"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Full Name'}), required=True) 
    username = forms.CharField(label=_("Username"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Username'}), required=True) 
    password_1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput({ 'class': 'form-control', 'placeholder':'Password'}), required=True) 
    password_2 = forms.CharField(label=_("Retype Password"), widget=forms.PasswordInput({ 'class': 'form-control', 'placeholder':'Retype Password'}), required=True) 
    access_key = forms.CharField(label=_("Access Key"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Access Key'}), required=True) 
    doctor_patient_choice = forms.ChoiceField(label=_("Role"), widget=forms.RadioSelect, choices=[('doctor', 'Doctor'), ('patient', 'Patient')], required=True)
    patients_doctor_username = forms.CharField(label=_("Doctor's Username*"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder': "Doctor's Username"}), required=False) 

    def clean_username(self):
        # Check if the username hasn't been taken already.
        username = self.cleaned_data['username']

        try:
            # Username does already exist, invalid.
            username_exists = User.objects.get(username=username)
            raise forms.ValidationError(_('Username already taken. Please try a different one.'), code='invalid')

        except User.DoesNotExist:
            # Username does not already exist, it's valid.
            pass

        return username 

    def clean_access_key(self):
        # Check if the username hasn't been taken already.
        access_key = self.cleaned_data['access_key']

        # Check if valid access key. Reading from access_keys.txt from project root.
        access_keys_file = open(os.path.join(settings.PROJECT_ROOT, 'access_keys.txt'))
        access_keys_list = access_keys_file.read().splitlines()

        if access_key not in access_keys_list:
            raise forms.ValidationError(_('Invalid access key.'), code='invalid')

        return access_key 

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()

        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')

        doctor_patient_choice = cleaned_data.get('doctor_patient_choice')
        patients_doctor_username = cleaned_data.get('patients_doctor_username')

        # Check if they typed and confirmed the password correctly.
        if password_1 != password_2:
            self.add_error('password_1', forms.ValidationError(_('Passwords must match.')))
            self.add_error('password_2', forms.ValidationError(_('Passwords must match.')))

        # Check if valid doctor username when signing up a patient. Need to 
        # assign the patient to a doctor upon creation.
        if doctor_patient_choice == 'patient':

            # Check if patients_doctor_username is a valid doctor's username.
            try:
                user = User.objects.get(username=patients_doctor_username)

                try:
                    Doctor.objects.get(user=user)
                except Doctor.DoesNotExist:
                    self.add_error('patients_doctor_username', forms.ValidationError(_('Doctor username not found.')))

            except User.DoesNotExist:
                self.add_error('patients_doctor_username', forms.ValidationError(_('Doctor username not found.')))


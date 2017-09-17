"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings 

from django.contrib.auth.models import User
from app.models import Doctor, Patient

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget, PhoneNumberPrefixWidget

import os

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   "class": "form-control",
                                   "placeholder": "Username"}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   "class": "form-control",
                                   "placeholder":"Password"}))

class QueryPatientsForm(forms.Form):
    """ Queries for patients by name"""
    patient_query = forms.CharField(label=_("Search"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Search for patient")})) 
    following = forms.BooleanField(label=_("Following"), widget=forms.CheckboxInput(), required=False)

class AddVideoForm(forms.Form):
    """ Queries for patients by name"""
    url = forms.CharField(label=_("URL"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Video url")})) 

class PatientNotesForm(forms.Form):
    """ Notes on a patient """
    notes = forms.CharField(widget=forms.Textarea({ "class": "form-control", "placeholder":_("Add notes here.")}), label="") 

class CreateNotificationForm(forms.Form):
    ESAS = "ESAS"
    PAIN = "Pain"
    MEDICATION = "Medication"
    OTHER = "Other"
    CATEGORY_CHOICES = (
        ("esas", "ESAS"),
        ("pain", "Pain"),
        ("medication", "Medication"),
        ("other", "Other"),
    )

    category = forms.ChoiceField(label=_("Select Category"), choices=CATEGORY_CHOICES, widget=forms.RadioSelect())
    text = forms.CharField(label=_("Text"), widget=forms.Textarea({"class": "form-control"}))

class CreateMedicationForm(forms.Form):

    POSOLOGY_CHOICES = (
        ('0', '0h'),
        ('2', '2h'),
        ('4', '4h'),
        ('6', '6h'),
        ('8', '8h'),
        ('10', '10h'),
        ('12', '12h'),
        ('14', '14h'),
        ('16', '16h'),
        ('18', '18h'),
        ('20', '20h'),
        ('22', '22h'),
    )

    name = forms.CharField(label=_("Name"), widget=forms.TextInput({"class": "form-control"}), required=True) 
    form = forms.CharField(label=_("Form"), widget=forms.TextInput({"class": "form-control"}), required=True) 
    dose = forms.CharField(label=_("Dose"), widget=forms.TextInput({"class": "form-control"}), required=True) 
    posology = forms.CharField(label=_("Posology"), widget=forms.TextInput({"class": "form-control"}), required=True) 
    #posology = forms.MultipleChoiceField(label=_("Posology"), widget=forms.CheckboxSelectMultiple, choices=POSOLOGY_CHOICES, required=True) 
    rescue = forms.CharField(label=_("Rescue"), widget=forms.TextInput({"class": "form-control"}), required=True) 

class UploadImageForm(forms.Form):
    image = forms.ImageField(label=_("Select a image."))


class SignupForm(forms.Form):
    """ Registering new users, both doctors and patients. """

    #doctor_patient_choice = forms.ChoiceField(label=_("Role"), widget=forms.RadioSelect, choices=[("doctor", "Doctor"), ("patient", "Patient")], required=True)
    full_name = forms.CharField(label=_("Full Name"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Full Name")}), required=True) 
    username = forms.CharField(label=_("Username"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Username")}), required=True) 
    telephone = forms.CharField(label=_("Telephone"), widget=forms.TextInput({"class": "form-control", "placeholder": _("Telephone")}), required=True)
    password_1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput({"class": "form-control", "placeholder":_("Password")}), required=True) 
    password_2 = forms.CharField(label=_("Retype Password"), widget=forms.PasswordInput({"class": "form-control", "placeholder":_("Retype Password")}), required=True) 
    access_key = forms.CharField(label=_("Access Key"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Access Key")}), required=True) 

    def clean_username(self):
        # Check if the username hasn't been taken already.
        username = self.cleaned_data["username"]

        try:
            # Username does already exist, invalid.
            username_exists = User.objects.get(username=username)
            raise forms.ValidationError(_("Username already taken. Please try a different one."), code="invalid")

        except User.DoesNotExist:
            # Username does not already exist, it's valid.
            pass

        return username 

    def clean_access_key(self):
        # Check if the username hasn't been taken already.
        access_key = self.cleaned_data["access_key"]

        # Check if valid access key. Reading from access_keys.txt from project root.
        access_keys_file = open(os.path.join(settings.PROJECT_ROOT, "access_keys.txt"))
        access_keys_list = access_keys_file.read().splitlines()

        if access_key not in access_keys_list:
            raise forms.ValidationError(_("Invalid access key."), code="invalid")

        return access_key 

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()

        password_1 = cleaned_data.get("password_1")
        password_2 = cleaned_data.get("password_2")

        # Check if they typed and confirmed the password correctly.
        if password_1 != password_2:
            self.add_error("password_1", forms.ValidationError(_("Passwords must match.")))
            self.add_error("password_2", forms.ValidationError(_("Passwords must match.")))

        return cleaned_data


class PatientSignupForm(SignupForm):
    hospital_id = forms.CharField(label=_("Hospital ID"), widget=forms.TextInput({"class": "form-control", "placeholder": _("Hospital ID")}), required=True) 
    age = forms.IntegerField(label=_("Age"), widget=forms.TextInput({"class": "form-control", "placeholder": _("Age")}), required=True)
    gender = forms.ChoiceField(label=_("Gender"), widget=forms.RadioSelect, choices=Patient.GENDER_CHOICES, required=True)
    city_of_residence = forms.CharField(label=_("City of Residence"), widget=forms.TextInput({"class": "form-control", "placeholder": _("City of Residence")}), required=True) 
    caregiver_name = forms.CharField(label=_("Caregiver Name"), widget=forms.TextInput({"class": "form-control", "placeholder": _("Caregiver Name")}), required=True) 
    caregiver_relationships= forms.CharField(label=_("Caregiver Relationships"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Caregiver Relationships")}), required=True)
    treatment_type = forms.ChoiceField(label=_("Treatment Type"), widget=forms.RadioSelect, choices=Patient.TREATMENT_CHOICES, required=True)
    tumor_type = forms.CharField(label=_("Tumor Type"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Tumor Type")}), required=True)
    comorbidities = forms.CharField(label=_("Comorbidities"), widget=forms.TextInput({"class": "form-control", "placeholder":_("Comorbidities")}), required=True)
    patients_doctor_username = forms.CharField(label=_("Your Doctor's Username"), widget=forms.TextInput({ "class": "form-control", "placeholder": _("Your Doctor's Username")}), required=True) 


    def clean(self):
        cleaned_data = super(PatientSignupForm, self).clean()

        patients_doctor_username = cleaned_data.get("patients_doctor_username")

        # Check if valid doctor username when signing up a patient. Need to 
        # assign the patient to a doctor upon creation.

        # Check if patients_doctor_username is a valid doctor's username.
        try:
            user = User.objects.get(username=patients_doctor_username)

            try:
                Doctor.objects.get(user=user)
            except Doctor.DoesNotExist:
                self.add_error("patients_doctor_username", forms.ValidationError(_("Doctor username not found.")))

        except User.DoesNotExist:
            self.add_error("patients_doctor_username", forms.ValidationError(_("Doctor username not found.")))

class EditPatientForm(forms.Form):
    hospital_id = forms.CharField(
            label=_("Hospital ID"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Hospital ID")}), 
            required=False) 
    full_name = forms.CharField(
            label=_("Full Name"), 
            widget=forms.TextInput({"class": "form-control", "placeholder":_("Name")}), 
            required=False) 
    telephone = forms.CharField(
            label=_("Telephone"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Telephone")}),
            required=False) 
    age = forms.IntegerField(
            label=_("Age"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Age")}), 
            required=False)
    gender = forms.ChoiceField(
            label=_("Gender"), 
            widget=forms.RadioSelect, 
            choices=Patient.GENDER_CHOICES, 
            required=False)
    city_of_residence = forms.CharField(
            label=_("City of Residence"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("City of Residence")}), 
            required=False) 
    caregiver_name = forms.CharField(
            label=_("Caregiver"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Caregiver")}), 
            required=False) 
    treatment_type = forms.ChoiceField(
            label=_("Treatment Type"), 
            widget=forms.RadioSelect, choices=Patient.TREATMENT_CHOICES, 
            required=False)
    next_appointment = forms.DateTimeField(
            label=_("Next Appointment"), 
            widget=forms.DateTimeInput({"class": "form-control", "placeholder": _("Next Appointment")}), 
            required=False)
    esas_alert = forms.IntegerField(
            label=_("ESAS Alert Level"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("ESAS Alert Level")}), 
            required=False)
    tumor_type = forms.CharField(
            label=_("Tumor Type"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Tumor Type")}),
            required=False) 
    comorbidities = forms.CharField(
            label=_("Comorbidities"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Comorbidities")}),
            required=False) 
    caregiver_relationships = forms.CharField(
            label=_("Caregiver Relationships"), 
            widget=forms.TextInput({"class": "form-control", "placeholder": _("Caregiver Relationships")}),
            required=False) 
    pk = forms.IntegerField(widget=forms.HiddenInput(), required=True)






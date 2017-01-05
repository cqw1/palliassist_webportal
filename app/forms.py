"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

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
    name_query = forms.CharField(label=_("Search"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Patient Name'})) 

class SignUpForm(forms.Form):
    """ Queries for patients by name"""
    real_name = forms.CharField(label=_("Full Name"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Full Name'})) 
    username = forms.CharField(label=_("Username"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Username'})) 
    password_1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput({ 'class': 'form-control', 'placeholder':'Password'})) 
    password_2 = forms.CharField(label=_("Retype Password"), widget=forms.PasswordInput({ 'class': 'form-control', 'placeholder':'Retype Password'})) 
    access_key = forms.CharField(label=_("Access Key"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder':'Access Key'})) 
    doctor_patient_choice = forms.ChoiceField(label=_("Role"), widget=forms.RadioSelect, choices=[('doctor', 'Doctor'), ('patient', 'Patient')])
    patients_doctor_username = forms.CharField(label=_("Doctor's Username*"), widget=forms.TextInput({ 'class': 'form-control', 'placeholder': "Doctor's Username"})) 
    #favorite_colors = forms.MultipleChoiceField( required=False, widget=forms.CheckboxSelectMultiple, choices=FAVORITE_COLORS_CHOICES,)


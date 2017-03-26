"""
Definition of urls for django_get_started.
"""

from datetime import datetime
from django.conf.urls import *
from app.forms import BootstrapAuthenticationForm
from app import views as app_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    #url(r'^(?i)$', app_views.home, name='home'),
    url(r'^(?i)$',
        app_views.login_redirect,
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Login',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^(?i)dashboard$', app_views.dashboard, name='dashboard'),
    url(r'^(?i)patients', app_views.patients, name='patients'),
    url(r'^(?i)patient-profile', app_views.patient_profile, name='patient-profile'),
    url(r'^(?i)signup-success', app_views.signup_success, name='signup-success'),
    url(r'^(?i)signup', app_views.signup, name='signup'),
    url(r'^(?i)messages', app_views.messages, name='messages'),
    url(r'^(?i)save-message', app_views.save_message, name='save-message'),
    url(r'^(?i)save-notes', app_views.save_notes, name='save-notes'),
    url(r'^(?i)create-channel', app_views.create_channel, name='create-channel'),
    url(r'^(?i)create-notification', app_views.create_notification, name='create-notification'),
    url(r'^(?i)delete-notification', app_views.delete_notification, name='delete-notification'),
    url(r'^(?i)create-medication', app_views.create_medication, name='create-medication'),
    url(r'^(?i)delete-medication', app_views.delete_medication, name='delete-medication'),
    url(r'^(?i)upload-image', app_views.upload_image, name='upload-image'),
    url(r'^(?i)sync-redcap', app_views.sync_redcap, name='sync-redcap'),
    url(r'^(?i)admin-input', app_views.admin_input, name='admin-input'),
    url(r'^(?i)mobile', app_views.mobile, name='mobile'),
    url(r'^(?i)token', app_views.token, name='token'),
    url(r'^(?i)login/$',
        auth_views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Login',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^(?i)logout$',
        auth_views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

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

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    #url(r'^$', app_views.home, name='home'),
    url(r'^$',
        app_views.loginRedirect,
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
    url(r'^dashboard$', app_views.dashboard, name='dashboard'),
    url(r'^patients', app_views.patients, name='patients'),
    url(r'^messages', app_views.messages, name='messages'),
    url(r'^saveMessage', app_views.saveMessage, name='saveMessage'),
    url(r'^token', app_views.token, name='token'),
    url(r'^login/$',
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
    url(r'^logout$',
        auth_views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

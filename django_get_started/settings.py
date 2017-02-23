"""
Django settings for django_get_started project.
"""

from os import path
from redcap import Project, RedcapError

from twilio.access_token import AccessToken, IpMessagingGrant
from twilio.rest.ip_messaging import TwilioIpMessagingClient
from twilio.rest import TwilioRestClient

from azure.storage.blob import BlockBlobService

PROJECT_ROOT = path.dirname(path.abspath(path.dirname(__file__)))

USER_URL = 'https://hcbredcap.com.br/api/'
USER_TOKEN = 'F2C5AEE8A2594B0A9E442EE91C56CC7A'

REDCAP_USER_PROJECT = Project(USER_URL, USER_TOKEN)

# get credentials for environment variables
TWILIO_ACCOUNT_SID = 'ACbf05fc8a591d9136132c9d62d8319eb1'
TWILIO_AUTH_TOKEN = '09f9ba77cd7c40b602cab2f484e58c07'
TWILIO_API_SECRET = 'R3W2DYt3Eq1hbwj2GRKQV531XeVDU9sJ'

TWILIO_API_KEY = 'SKeed5a60867e8f918ac7f2e9fa819d98a'
TWILIO_IPM_SERVICE_SID = 'IS2ec68050ef5e4c79b15b78c3ded7ddc5'

# old one with testchannel nd general
#TWILIO_SERVICE_SID = 'IS7d421d86df064d9698e91ee6e3d4bcf5'

# Initialize the client
TWILIO_IPM_CLIENT = TwilioIpMessagingClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
TWILIO_IPM_SERVICE = TWILIO_IPM_CLIENT.services.get(sid=TWILIO_IPM_SERVICE_SID)

BLOCK_BLOB_SERVICE = BlockBlobService(account_name="palliassistblobstorage", account_key="r9tHMEj5VV/PwJyjN3KYySUqsnq9tCrxh6kDKFvVY3vrm+GluHN/a1LQjXKYIUzoHEle7x3EyIQwoOijzRJiOA==")


DEBUG = True 
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = (
    'localhost',
    'palliassist-dev-us.azurewebsites.net',
    '127.0.0.1',
    '599632a7.ngrok.io',
    '*',
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

AUTHENTICATION_BACKENDS = ('app.backends.REDCapBackend',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(PROJECT_ROOT, 'db.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = 'dashboard'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = ''
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = ''
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static').replace('\\', '/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #path.join(PROJECT_ROOT, 'app/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wgwpi492e$8_erx+d)!tpeoim'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'django_get_started.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'django_get_started.wsgi.application'

TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        path.join(path.dirname(__file__), 'templates'),
        PROJECT_ROOT + '/app/templates/app',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
},
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'phonenumber_field',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Specify the default test runner.
TEST_RUNNER = 'django.test.runner.DiscoverRunner'


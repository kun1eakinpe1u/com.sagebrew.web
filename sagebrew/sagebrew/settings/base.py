' Django default settings for automated_test_client project.'
from __future__ import absolute_import

from os import environ
from unipath import Path
from datetime import timedelta

PROJECT_DIR = Path(__file__).ancestor(3)
MEDIA_ROOT = PROJECT_DIR.child("media")
STATIC_ROOT = PROJECT_DIR.child("static")

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Devon Bleibtrey', 'bleib1dj@gmail.com'),
)

environ['HTTPS'] = "on"
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

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
# Example: "/var/www/example.com/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/sagebrew/static/' % PROJECT_DIR,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.


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
    'djangosecure.middleware.SecurityMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'sagebrew.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'sagebrew.wsgi.application'


TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '%s/sagebrew/templates/'  % PROJECT_DIR,
)

FIXTURE_DIRS = (
    '%s/sagebrew/fixtures/' % PROJECT_DIR,
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangosecure',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'south',
    'djcelery',
    'rest_framework',
    'admin_honeypot',
    'provider',
    'provider.oauth2',
    'storages',
    'localflavor',
)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
}

LOGIN_REDIRECT_URL = '/'
EMAIL_USE_TLS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ADMIN_HONEYPOT_EMAIL_ADMINS = False
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
APPEND_SLASH = True
OAUTH_SINGLE_ACCESS_TOKEN = False
#OAUTH_ENFORCE_SECURE = True
OAUTH_EXPIRE_DELTA = timedelta(days=30, minutes=0, seconds=0)
OAUTH_EXPIRE_DELTA_PUBLIC = timedelta(days=30, minutes=0, seconds=0)
OAUTH_DELETE_EXPIRED = True

CELERY_DEFAULT_QUEUE = "sagebrew-default"
#BROKER_URL = 'redis://localhost:6379/0'
BROKER_URL = 'amqp://sagebrew:this_is_the_sagebrew_password@localhost:5672//'
#BROKER_URL = 'ironmq://52dd5790f5137e0005000040:jXvMZvprwPw_dZPV1eYkbARcM64@'
#CELERY_RESULT_BACKEND = 'cache+memcached://127.0.0.1:11211/'
#CELERY_CACHE_BACKEND_OPTIONS = {'binary': True,
#                                'behaviors': {'tcp_nodelay': True}}
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
LOCAL_IP = "172.20.10.9"
BLUETOOTH_IP = '172.20.10.11'
#CELERY_RESULT_BACKEND = 'ironcache://52dd5790f5137e0005000040:jXvMZvprwPw_dZPV1eYkbARcM64@/automated_test_client'
#BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 600, 'fanout_prefix': True}
#CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_DISABLE_RATE_LIMITS=True
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_IMPORTS = ()
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_IGNORE_RESULT = False
CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1
# celery -A automated_test_client worker -l info
# celery -A automated_test_client beat -l info

# need to set usb device filter (http://forum.xda-developers.com/showthread.php?t=570452)
# Make sure no left over scheduled tests in periodic test portion of DB
# Make sure USB is hooked up to vm via ./adb devices
# sudo apt-get install winbind
# sudo pico /etc/nsswitch.conf
#    Append wins to the end of the line with `hosts:` in it 
#	     hosts:          files dns wins
#        Save the file 
# sudo apt-get install samba
CELERYBEAT_SCHEDULE = {}
CELERY_TIMEZONE = 'UTC'

import djcelery
import iron_celery

djcelery.setup_loader()

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
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

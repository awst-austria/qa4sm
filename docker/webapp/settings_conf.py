## Settings file for environment specific config variables.
## Will be imported from settings.py

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pr5d*hccyy)ut=25mjx*-_&17esjrkmi&x==wm45#=(38485qd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATA_FOLDER = '/var/lib/qa4sm-web-val/valentina/data/'

# LOG_DIR value in install.sh should point to the same folder
LOG_FILE = '/var/log/valentina/valentina.log'

ALLOWED_HOSTS = ['qa4sm.eodc.eu','localhost']

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

FORCE_SCRIPT_NAME = ''

#Celery settings
CELERY_BROKER_URL='pyamqp://guest:guest@qa4sm-rabbitmq'
CELERY_RESULT_BACKEND = 'redis://qa4sm-redis'
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_BROKER_TRANSPORT_OPTIONS = {'max_retries': 3,'interval_start': 1,'interval_step': 1,'interval_max': 3,}

DBSM = 'postgresql'
DB_PASSWORD = 'dkleycb5pq'

## Email settings
EMAIL_HOST = 'bsmtp.a1.net'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'qa4sm@awst.at'
EMAIL_FROM = 'qa4sm@awst.at'
EMAIL_USE_TLS = 'yes'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'qa4sm@awst.at'

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/app-messages'

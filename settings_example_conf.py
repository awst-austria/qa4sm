## Settings file for environment specific config variables.
## Will be imported from settings.py

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's3cr3t'
API_SECRET_KEY = '@P1 s3cr3t'

SITE_URL = "https://qa4sm.eu"

DOI_ACCESS_TOKEN = 'notset'
DOI_REGISTRATION_URL = "https://zenodo.org/api/deposit/depositions"
DOI_URL_PREFIX = "https://doi.org/"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


LOG_FILE = 'valentina.log'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

FORCE_SCRIPT_NAME = ''

#Celery settings
CELERY_BROKER_URL='pyamqp://'
CELERY_RESULT_BACKEND = 'redis://localhost'
CELERY_ACCEPT_CONTENT = ['json','pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_BROKER_TRANSPORT_OPTIONS = {'max_retries': 3,'interval_start': 1,'interval_step': 1,'interval_max': 3,}

DBSM = 'sqlite'
DB_PASSWORD = 's3cr3t'


## Email settings
EMAIL_HOST = 'smtp.ionos.de'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'support@qa4sm.eu'
EMAIL_FROM = 'support@qa4sm.eu'
EMAIL_USE_TLS = 'yes'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'support@qa4sm.eu'

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/tmp/app-messages'
USER_DATA_DIR = '/var/lib/qa4sm-web-val/valentina/data/user_data'
USER_MANUAL_PATH = '/var/lib/qa4sm-web-val/valentina/user_manual/user_manual.pdf'
#!/bin/bash

## Script to generate usable config from example config file. Takes an optional argument, e.g. "ops" or "jenkins" or "dev"

DIRNAME=$(dirname "$0")

ENV="ops"
if [ $# -ge 1 ]; then
    ENV="$1"
fi

NEWKEY=$(python -c "import django.core.management.utils; print(django.core.management.utils.get_random_secret_key())")
## escape special RHS sed symbols, otherwise they cause problems in the sed expression below
NEWKEY=${NEWKEY//\\/\\\\}
NEWKEY=${NEWKEY//&/\\&}

# default values (for ops)
LOGFILE="/var/log/valentina/valentina.log"
DEBUGFLAG="False"
ALLOWED_HOSTS="['qa4sm.eodc.eu','localhost']"
STATIC_URL='/static/'
MEDIA_URL='/media/'
FORCE_SCRIPT_NAME=''
SSL_SECURITY=""
DATA_FOLDER="/var/lib/qa4sm-web-val/valentina/data/"


DB_PASSWORD=""
EMAIL_PASSWORD=""
if [[ -e ~/valentina_db_password ]]; then
    read -r DB_PASSWORD<~/valentina_db_password
fi

if [[ -e ~/valentina_email_password ]]; then
    read -r EMAIL_PASSWORD<~/valentina_email_password
fi

DBSM="postgresql"

if [ "x$ENV" == "xjenkins" ]; then
    LOGFILE="valentina.log"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    STATIC_URL='/static/'
    MEDIA_URL='/media/'
    FORCE_SCRIPT_NAME=''
    DEBUGFLAG="True"
    SSL_SECURITY=""
    DATA_FOLDER="/data/qa4sm/data/"
fi

if [ "x$ENV" == "xdev" ]; then
    STATIC_URL='/static/'
    MEDIA_URL='/media/'
    FORCE_SCRIPT_NAME=''
    DEBUGFLAG="True"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    SSL_SECURITY=""
    DATA_FOLDER="/data/qa4sm/data/"
    DBSM="sqlite"
fi

sed -e "s|^[ ]*EMAIL_HOST_PASSWORD = .*$|EMAIL_HOST_PASSWORD = '$EMAIL_PASSWORD'|g;s|^[ ]*DBSM = .*$|DBSM = '$DBSM'|g;s|^[ ]*DB_PASSWORD = .*$|DB_PASSWORD = '$DB_PASSWORD'|g;s|^[ ]*MEDIA_URL = .*$|MEDIA_URL = '$MEDIA_URL'|g;s|^[ ]*DATA_FOLDER = .*$|DATA_FOLDER = '$DATA_FOLDER'|g;s|^[ ]*STATIC_URL = .*$|STATIC_URL = '$STATIC_URL'|g;s|^[ ]*FORCE_SCRIPT_NAME = .*$|FORCE_SCRIPT_NAME = '$FORCE_SCRIPT_NAME'|g;s|^[ ]*SECRET_KEY = .*$|SECRET_KEY = '$NEWKEY'|g;s|^[ ]*DEBUG =.*$|DEBUG = $DEBUGFLAG|g;s|^[ ]*LOG_FILE = .*$|LOG_FILE = '$LOGFILE'|g;s|^[ ]*ALLOWED_HOSTS =.*$|ALLOWED_HOSTS = ${ALLOWED_HOSTS}${SSL_SECURITY}|g" $DIRNAME/settings_example_conf.py > $DIRNAME/valentina/settings_conf.py

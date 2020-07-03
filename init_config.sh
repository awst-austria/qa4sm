#!/bin/bash

## Script to generate usable config from example config file. Takes an optional argument, e.g. "ops" or "jenkins" or "dev" or "test"

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
ALLOWED_HOSTS="['qa4sm.eu','localhost']"
STATIC_URL='/static/'
MEDIA_URL='/media/'
FORCE_SCRIPT_NAME=''
SSL_SECURITY=""

# this token needs to be set as an evironment variable when this script is run
# e.g. in the CI (Jenkins credentials or Travis secrets)
if [ "x$DOI_ACCESS_TOKEN_ENV" == "x" ]; then
    export DOI_ACCESS_TOKEN_ENV="notset"
fi

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
    DBSM="sqlite"
fi

if [ "x$ENV" == "xdev" ]; then
    STATIC_URL='/static/'
    MEDIA_URL='/media/'
    FORCE_SCRIPT_NAME=''
    DEBUGFLAG="True"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    SSL_SECURITY=""
    DBSM="sqlite"
fi

if [ "x$ENV" == "xtest" ]; then
    STATIC_URL='/static/'
    MEDIA_URL='/media/'
    FORCE_SCRIPT_NAME=''
    DEBUGFLAG="True"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    SSL_SECURITY=""
    DBSM="sqlite"
    LOGFILE="/tmp/log/valentina/valentina.log"
fi


sed -e "s|^[ ]*EMAIL_HOST_PASSWORD = .*$|EMAIL_HOST_PASSWORD = '$EMAIL_PASSWORD'|g;s|^[ ]*DBSM = .*$|DBSM = '$DBSM'|g;s|^[ ]*DB_PASSWORD = .*$|DB_PASSWORD = '$DB_PASSWORD'|g;s|^[ ]*MEDIA_URL = .*$|MEDIA_URL = '$MEDIA_URL'|g;s|^[ ]*STATIC_URL = .*$|STATIC_URL = '$STATIC_URL'|g;s|^[ ]*FORCE_SCRIPT_NAME = .*$|FORCE_SCRIPT_NAME = '$FORCE_SCRIPT_NAME'|g;s|^[ ]*SECRET_KEY = .*$|SECRET_KEY = '$NEWKEY'|g;s|^[ ]*DEBUG =.*$|DEBUG = $DEBUGFLAG|g;s|^[ ]*LOG_FILE = .*$|LOG_FILE = '$LOGFILE'|g;s|^[ ]*ALLOWED_HOSTS =.*$|ALLOWED_HOSTS = ${ALLOWED_HOSTS}${SSL_SECURITY}|g;s|^[ ]*DOI_ACCESS_TOKEN = .*$|DOI_ACCESS_TOKEN = '$DOI_ACCESS_TOKEN_ENV'|g" $DIRNAME/settings_example_conf.py > $DIRNAME/valentina/settings_conf.py

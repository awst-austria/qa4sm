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
SITE_URL="https://qa4sm.eu"
LOGFILE="/var/log/valentina/valentina.log"
DEBUGFLAG="False"
ALLOWED_HOSTS="['qa4sm.eu','localhost']"
STATIC_URL='/static/'
MEDIA_URL='/media/'
FORCE_SCRIPT_NAME=''
SSL_SECURITY=""
DOI_REGISTRATION_URL="https://zenodo.org/api/deposit/depositions"
USER_DATA_DIR='/var/lib/qa4sm-web-val/valentina/data/user_data'
USER_MANUAL_PATH='/var/lib/qa4sm-web-val/valentina/user_manual/user_manual.pdf'

# this token needs to be set as an evironment variable when this script is run
# e.g. in the CI (Jenkins credentials or Travis secrets)
if [ "x$DOI_ACCESS_TOKEN_ENV" == "x" ]; then
    export DOI_ACCESS_TOKEN_ENV="notset"
fi

# this token needs to be set as an evironment variable when this script is run
# e.g. in the CI (Jenkins credentials or Travis secrets)
if [ "x$ADMIN_ACCESS_TOKEN" == "x" ]; then
    export ADMIN_ACCESS_TOKEN="notset"
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
    DEBUGFLAG="True"
    SSL_SECURITY=""
    DBSM="sqlite"
    DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions"
    USER_DATA_DIR="${DIRNAME}/testdata/user_data/"
    USER_MANUAL_PATH="${DIRNAME}/user_manual/user_manual.pdf"
fi

if [ "x$ENV" == "xdev" ]; then
    DEBUGFLAG="True"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    SSL_SECURITY=""
    DBSM="sqlite"
    DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions"
    USER_DATA_DIR="${DIRNAME}/testdata/user_data/"
    USER_MANUAL_PATH="${DIRNAME}/user_manual/user_manual.pdf"
fi

if [ "x$ENV" == "xtest" ]; then
    DEBUGFLAG="True"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost']"
    SSL_SECURITY=""
    DBSM="sqlite"
    LOGFILE="/tmp/log/valentina/valentina.log"
    DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions"
    USER_DATA_DIR="${DIRNAME}/testdata/user_data/"
    USER_MANUAL_PATH="${DIRNAME}/user_manual/user_manual.pdf"
fi

if [ "x$ENV" == "xtestenv" ]; then
    SITE_URL="https://test.qa4sm.eu"
    DEBUGFLAG="False"
    ALLOWED_HOSTS="['127.0.0.1', 'localhost', '10.48.108.24', 'test.qa4sm.eu', '10.10.10.66','test2.qa4sm.eu']"
    DOI_REGISTRATION_URL="https://sandbox.zenodo.org/api/deposit/depositions"
    USER_DATA_DIR='/var/lib/qa4sm-web-val/valentina/data/user_data'
    USER_MANUAL_PATH='/var/lib/qa4sm-web-val/valentina/user_manual/user_manual.pdf'
fi

echo $DOI_ACCESS_TOKEN_ENV
echo $ADMIN_ACCESS_TOKEN

sed -e "s|^[ ]*USER_MANUAL_PATH = .*$|USER_MANUAL_PATH = '$USER_MANUAL_PATH'|g;s|^[ ]*USER_DATA_DIR = .*$|USER_DATA_DIR = '$USER_DATA_DIR'|g;s|^[ ]*DOI_ACCESS_TOKEN = .*$|DOI_ACCESS_TOKEN = '$DOI_ACCESS_TOKEN_ENV'|g;s|^[ ]*ADMIN_ACCESS_TOKEN = .*$|ADMIN_ACCESS_TOKEN = '$ADMIN_ACCESS_TOKEN'|g;s|^[ ]*DOI_REGISTRATION_URL = .*$|DOI_REGISTRATION_URL = '$DOI_REGISTRATION_URL'|g;s|^[ ]*SITE_URL = .*$|SITE_URL = '$SITE_URL'|g;s|^[ ]*EMAIL_HOST_PASSWORD = .*$|EMAIL_HOST_PASSWORD = '$EMAIL_PASSWORD'|g;s|^[ ]*DBSM = .*$|DBSM = '$DBSM'|g;s|^[ ]*DB_PASSWORD = .*$|DB_PASSWORD = '$DB_PASSWORD'|g;s|^[ ]*MEDIA_URL = .*$|MEDIA_URL = '$MEDIA_URL'|g;s|^[ ]*STATIC_URL = .*$|STATIC_URL = '$STATIC_URL'|g;s|^[ ]*FORCE_SCRIPT_NAME = .*$|FORCE_SCRIPT_NAME = '$FORCE_SCRIPT_NAME'|g;s|^[ ]*SECRET_KEY = .*$|SECRET_KEY = '$NEWKEY'|g;s|^[ ]*DEBUG =.*$|DEBUG = $DEBUGFLAG|g;s|^[ ]*LOG_FILE = .*$|LOG_FILE = '$LOGFILE'|g;s|^[ ]*ALLOWED_HOSTS =.*$|ALLOWED_HOSTS = ${ALLOWED_HOSTS}${SSL_SECURITY}|g;" $DIRNAME/settings_example_conf.py > $DIRNAME/valentina/settings_conf.py

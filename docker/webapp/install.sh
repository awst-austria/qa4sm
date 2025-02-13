#!/bin/bash
set -e
set -x
WEB_VAL_GIT_DIR="/tmp/qa4sm-git"
APP_DIR="/var/lib/qa4sm-web-val/valentina"
LOG_DIR="/var/log/valentina"
LOG_FILE="$LOG_DIR/valentina.log"
mkdir -p "$APP_DIR"
mkdir "$APP_DIR/db_dump"
mkdir $LOG_DIR
touch $LOG_FILE
chown root:www-data -R $LOG_DIR
chmod ug+rwx -R $LOG_DIR

rsync -r "$WEB_VAL_GIT_DIR/" "$APP_DIR/" --exclude="tests" --exclude="db.sqlite3"
ls "$WEB_VAL_GIT_DIR/docker/"
ls "$WEB_VAL_GIT_DIR/docker/webapp"
cp "$WEB_VAL_GIT_DIR/docker/webapp/apache.conf" /etc/apache2/sites-available/qa4sm-app.conf
chown www-data:www-data -R "$APP_DIR"
a2dissite 000-default
a2ensite qa4sm-app
. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
pip install mod_wsgi
pip install --no-deps smos==0.3.1
mod_wsgi-express module-config
# a2dismod wsgi
# rm /usr/lib/apache2/modules/mod_wsgi.so
# cp /var/lib/qa4sm-web-val/virtenv/lib/python3.8/site-packages/mod_wsgi/server/mod_wsgi-py38.cpython-38m-x86_64-linux-gnu.so /usr/lib/apache2/modules/mod_wsgi.so
a2enmod wsgi && a2enmod headers

#!/bin/bash
set -e
set -x
WEB_VAL_GIT_DIR="/tmp/qa4sm-git"
APP_DIR="/var/lib/qa4sm-web-val/valentina"
mkdir -p "$APP_DIR"
wget -P /tmp/ https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda && ln -s /opt/miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && rm /tmp/Miniconda3-latest-Linux-x86_64.sh
rsync -r "$WEB_VAL_GIT_DIR/" "$APP_DIR/" --exclude="tests" --exclude="db.sqlite3"
cp "$WEB_VAL_GIT_DIR/docker/qa4sm-webapp/apache.conf" /etc/apache2/sites-available/qa4sm-app.conf
a2ensite qa4sm-app
/opt/miniconda/condabin/conda env create --prefix=/var/lib/qa4sm-conda -f "$WEB_VAL_GIT_DIR/environment/qa4sm_env.yml"
. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-conda
pip install mod_wsgi
mod_wsgi-express module-config
a2dismod wsgi
rm /usr/lib/apache2/modules/mod_wsgi.so
cp /var/lib/qa4sm-conda/lib/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-x86_64-linux-gnu.so /usr/lib/apache2/modules/mod_wsgi.so
a2enmod wsgi && a2enmod headers
#!/bin/bash
set -e
set -x
export PIP_USE_PEP517=1
WEB_VAL_GIT_DIR="/tmp/qa4sm-git"
APP_DIR="/var/lib/qa4sm-web-val/valentina"
mkdir -p "$APP_DIR"

wget -P /tmp/ https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda && ln -s /opt/miniconda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && rm /tmp/Miniconda3-latest-Linux-x86_64.sh
rsync -r "$WEB_VAL_GIT_DIR/" "$APP_DIR/" --exclude="tests" --exclude="db.sqlite3"
/opt/miniconda/condabin/conda env create --prefix=/var/lib/qa4sm-web-val/virtenv -f "$WEB_VAL_GIT_DIR/environment/qa4sm_env.yml"

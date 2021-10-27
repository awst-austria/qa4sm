#!/bin/bash
set -e
set -x
WEB_VAL_GIT_DIR="/tmp/qa4sm-git"
APP_DIR="/var/lib/qa4sm-web-val/valentina"
mkdir -p "$APP_DIR"

rsync -r "$WEB_VAL_GIT_DIR/" "$APP_DIR/" --exclude="tests" --exclude="db.sqlite3"
/opt/miniconda/condabin/conda env create --prefix=/var/lib/qa4sm-web-val/virtenv -f "$WEB_VAL_GIT_DIR/environment/qa4sm_env.yml"

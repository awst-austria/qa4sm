#!/bin/bash
echo "Auto cleanup"
APP_DIR="/var/lib/qa4sm-web-val"
MINICONDA_PATH="/opt/miniconda"
PYTHON_ENV_DIR="$APP_DIR/virtenv"

PATH="$PATH:$MINICONDA_PATH/bin/"
source activate "$PYTHON_ENV_DIR"
cd "$APP_DIR/valentina"
python manage.py autocleanupvalidations

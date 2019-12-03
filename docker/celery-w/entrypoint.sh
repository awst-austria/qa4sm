#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
export C_FORCE_ROOT="true"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
ln -s /data/qa4sm/data /var/lib/qa4sm-web-val/valentina/data
mkdir run_celery
touch run_celery/celery.state.dat
cd $APP_DIR
celery -A valentina worker --max-tasks-per-child=1 --concurrency=$QA4SM_CELERY_WORKERS -l INFO --time-limit=16000 --prefetch-multiplier=1

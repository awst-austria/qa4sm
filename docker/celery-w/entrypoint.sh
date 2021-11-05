#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
export C_FORCE_ROOT="true"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
if [ ! -d "run_celery" ]; then
  mkdir run_celery
  touch run_celery/celery.state.dat
fi

cd $APP_DIR
MKL_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_DYNAMIC=FALSE
OPENBLAS_NUM_THREADS=1
if [ ! -d "/var/log/valentina" ]; then
  mkdir /var/log/valentina
fi
celery -A valentina worker --max-tasks-per-child=1 --concurrency=$QA4SM_CELERY_WORKERS -l INFO --time-limit=16000 --prefetch-multiplier=1

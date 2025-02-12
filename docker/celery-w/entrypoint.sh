#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
export C_FORCE_ROOT="true"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
pip install --no-deps smos==0.3.1
if [ ! -d "run_celery" ]; then
  mkdir run_celery
  touch run_celery/celery.state.dat
fi

cd $APP_DIR
git submodule update --init --recursive  validator/fixtures
git config --global --add safe.directory "$APP_DIR/validator/fixtures"
cd "validator/fixtures"
git checkout main

cd $APP_DIR
chown www-data:www-data -R "$APP_DIR/validator/fixtures"


if [ ! -d "/var/log/valentina" ]; then
  mkdir /var/log/valentina
fi
MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_DYNAMIC=FALSE OPENBLAS_NUM_THREADS=1 celery -A valentina worker --max-tasks-per-child=1 --concurrency=$QA4SM_CELERY_WORKERS -l INFO --time-limit=16000 --prefetch-multiplier=1

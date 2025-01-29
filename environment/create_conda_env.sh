#!/bin/bash

# Script that creates the conda/python environment for the web validation service and
# installs the service.
#
#Celery requires RabbitMQ and Redis installed locally. Since the Reddis package in the
# debain repository seems to be broken, Redis and RabitMQ has to be installed manually.

# install paths for miniconda and the app itself:
if [ "x$INSTALL_DIR" == "x" ]; then
    INSTALL_DIR="/var/lib/qa4sm-web-val"
fi
if [ "x$MINICONDA_PATH" == "x" ]; then
    MINICONDA_PATH="/opt/miniconda"
fi
if [ "x$TOOL_DIR" == "x" ]; then
    TOOL_DIR="/opt/tools"
fi
if [ "x$PYTHON_ENV_DIR" == "x" ]; then
    PYTHON_ENV_DIR="/var/lib/qa4sm-conda"
fi
if [ "x$VALENTINA_BRANCH" == "x" ]; then
    VALENTINA_BRANCH="master"
fi

# dir this script is in
THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo "$INSTALL_DIR, $MINICONDA_PATH, $TOOL_DIR, $PYTHON_ENV_DIR, $THIS_SCRIPT_DIR"

# external software
MINICONDA_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"

MINICONDA_PKG="$TOOL_DIR/miniconda.sh"

# tmp dir structure
TMP_BASE_DIR="/tmp/"
TEMP_DIR=$(mktemp -d -p $TMP_BASE_DIR -t "web-val.XXXXXXXX")
chmod 700 $TEMP_DIR
echo "Tmp dir: $TEMP_DIR"

# clean up
if [[ -e "$INSTALL_DIR" ]]; then
    rm -Rf "$INSTALL_DIR"
fi
if [[ -e "$PYTHON_ENV_DIR" ]]; then
    rm -Rf "$PYTHON_ENV_DIR"
fi

mkdir "$INSTALL_DIR"

#Install conda and create virtual env.
echo "Downloading miniconda installer"
# download only if newer than existing
if [ -e "$MINICONDA_PKG" ]; then
    ZFLAG="-z $MINICONDA_PKG"
else
    ZFLAG=""
fi
CONDA_HTTP_CODE=$(curl -L -s -w "%{http_code}" -o $MINICONDA_PKG $ZFLAG $MINICONDA_URL)
echo "$CONDA_HTTP_CODE"

# only install if new conda version
if [ "$CONDA_HTTP_CODE" != "304" ]; then
    echo "Installing miniconda"
    if [[ -e $MINICONDA_PATH ]]; then
        rm -Rf $MINICONDA_PATH
    fi
    bash $MINICONDA_PKG -b -p $MINICONDA_PATH
fi
export PATH="$MINICONDA_PATH/bin:$PATH"

# echo "Creating python virtual environment in $PYTHON_ENV_DIR"
conda create --yes --prefix $PYTHON_ENV_DIR -c conda-forge python=3.12 numpy>=2.0.0 scipy pandas>=2 cython pytest pip matplotlib pyproj django pyresample pygrib shapely cartopy xarray dask
source activate $PYTHON_ENV_DIR

# pip uninstall --yes shapely
# pip install --no-binary :all: shapely
pip install sqlparse
pip install sqlparse
pip install ascat
pip install c3s_sm
pip install esa_cci_sm
pip install smos
pip install ecmwf_models
pip install coverage
pip install pygeogrids
pip install pytest-django
pip install django-widget-tweaks
pip install psycopg2-binary
pip install pytest-cov
pip install pytest-mpl
pip install celery
pip install celery[redis]
pip install gldas
pip install smap-io
pip install django-countries
pip install seaborn
pip install --upgrade --force-reinstall netcdf4
pip install "pytesmo>=0.16.0"
pip install "ismn>=1.3.2"
pip install requests
pip install git+https://github.com/awst-austria/qa4sm-reader.git@check-master
pip install "qa4sm-preprocessing>=0.2.0"
pip install djangorestframework
pip install django_rest_passwordreset
pip install "numpy>=2.0.0"
pip install "pandas>=2"


cd $TEMP_DIR

#Clone the  web validation service repo
echo "Checking out code from branch $VALENTINA_BRANCH to $INSTALL_DIR"
git clone -b $VALENTINA_BRANCH --single-branch https://github.com/awst-austria/qa4sm.git "$INSTALL_DIR"

# clean up
rm -Rf $TEMP_DIR

echo "Installation ready in $INSTALL_DIR"

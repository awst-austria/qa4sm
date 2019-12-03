#!/bin/bash -xe

if [ $# -lt 2 ]; then
	echo "Usage: $0 <miniconda path> <python environment target directory>"
	exit 1
fi

MINICONDA_PATH="$1"
PYTHON_ENV_DIR="$2"

source $MINICONDA_PATH/etc/profile.d/conda.sh

echo "Creating conda environment in $PYTHON_ENV_DIR"
conda create --yes --prefix "$PYTHON_ENV_DIR" -c conda-forge python=3.6 numpy scipy pandas cython pytest pip matplotlib pyproj django pyresample pygrib cartopy
conda activate "$PYTHON_ENV_DIR"

export USE_CYTHON=True

pip uninstall --yes shapely
pip install --no-binary :all: shapely
pip install sqlparse
pip install pynetcf
pip install ascat
# pip install pybufr-ecmwf
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
pip install celery==4.1.1
pip install celery[redis]
pip install gldas
pip install smap-io
pip install django-countries
pip install seaborn
# export CFLAGS="-DACCEPT_USE_OF_DEPRECATED_PROJ_API_H=1"
# pip install cartopy
pip install --upgrade --force-reinstall netcdf4
pip install pytesmo
#pip install git+https://github.com/TUW-GEO/pytesmo.git
pip install ismn

conda env export --no-builds --prefix="$PYTHON_ENV_DIR" > qa4sm_env.yml
sed -i '/^prefix:/d' qa4sm_env.yml

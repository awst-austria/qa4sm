#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
PGPASSWORD="$POSTGRES_PASSWORD"
ADMIN_PASS="12admin34"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
export LD_LIBRARY_PATH=/var/lib/qa4sm-web-val/virtenv/lib
python $APP_DIR/manage.py collectstatic --noinput

# generate ISMN geojson files if they don't exist
DATA_FOLDER="${QA4SM_DATA_FOLDER}ISMN"
ls -d "$DATA_FOLDER"/*/ | while IFS= read -r dir; do
    echo "$dir"
    # Check if the directory contains "ismn_sensors.json"
    if [ -f "${dir}/ismn_sensors.json" ]; then
      # Print a message indicating the presence of "ismn_sensors.json"
      echo "'ismn_sensors.json' already exists in directory."
    else
      # Run the ISMN export_geojson command
      ismn export_geojson "${dir}" -f network -f station -f depth -f timerange -f frm_class
      echo "Created ismn_sensors.json in ${dir}"
    fi
done

# wait for the db to initialize
sleep 10s
NEW_DB="FALSE"
if psql -h qa4sm-db -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw $QA4SM_DB_NAME; then
    echo "DB exists"
else
	echo "DB does not exist, let's create it..."
	psql -h qa4sm-db -p 5432 -U postgres -q -c '\set ON_ERROR_STOP on' -c "CREATE DATABASE $QA4SM_DB_NAME;" -c "CREATE USER $QA4SM_DB_USER WITH ENCRYPTED PASSWORD '$QA4SM_DB_PASSWORD';" -c "GRANT ALL PRIVILEGES ON DATABASE $QA4SM_DB_NAME TO $QA4SM_DB_USER;"
	echo "DB has been created."
  NEW_DB="TRUE"
fi

if psql -h qa4sm-db -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw $QA4SM_DB_NAME; then
		echo "Running migrations"
		python $APP_DIR/manage.py migrate
    echo "Loading fixtures"
    python $APP_DIR/manage.py loaddata filters
	  python $APP_DIR/manage.py loaddata versions
	  python $APP_DIR/manage.py loaddata variables
	  python $APP_DIR/manage.py loaddata datasets
	  python $APP_DIR/manage.py loaddata networks
	  python $APP_DIR/manage.py setdatasetpaths --path /var/lib/qa4sm-web-val/valentina/data
	  python $APP_DIR/manage.py abortrunningvalidations
	  python $APP_DIR/manage.py cleancelerytasks
	  python $APP_DIR/manage.py generateismnlist

	if [ "$NEW_DB" = "TRUE" ]; then
      echo "Creating admin user"
      echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'qa4sm@awst.at', '$ADMIN_PASS')" | python $APP_DIR/manage.py shell
    fi

	else
		echo "DB does not exist"
		exit -1
	fi

if [ ! -d "/var/log/apache2" ]; then
  mkdir /var/log/apache2
  chown www-data:www-data /var/log/apache2
fi

if [ ! -d "/var/log/valentina" ]; then
  mkdir /var/log/valentina
fi
chown www-data:www-data -R /var/log/valentina

exec apachectl -D FOREGROUND

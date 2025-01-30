#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
PGPASSWORD="$POSTGRES_PASSWORD"
ADMIN_PASS="12admin34"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
pip install --no-deps smos==0.3.1
pip install --no-deps qa4sm-preprocessing==0.3
export LD_LIBRARY_PATH=/var/lib/qa4sm-web-val/virtenv/lib
python $APP_DIR/manage.py collectstatic --noinput


# this part is needed, so we are able to run commits on our fixtures ---
cd $APP_DIR
git config --global --add safe.directory $APP_DIR
git config --global --add safe.directory "$APP_DIR/validator/fixtures"

git submodule update --init --recursive  validator/fixtures
cd "validator/fixtures"
git checkout main

cd $APP_DIR
chown www-data:www-data -R "$APP_DIR/validator/fixtures"
chown www-data:www-data -R "$APP_DIR/.git/modules"
# -----------------------------------------------------------------------


# generate ISMN geojson files if they don't exist
DATA_FOLDER="/var/lib/qa4sm-web-val/valentina/data/ISMN"
ls -d "$DATA_FOLDER"/*/ | grep -v '2018' | while IFS= read -r dir; do
    echo "$dir"
    # Check if the directory contains "ismn_sensors.json"
    if [ -f "${dir}ismn_sensors.json" ]; then
      # Print a message indicating the presence of "ismn_sensors.json"
      echo "'ismn_sensors.json' already exists in directory."
    else
      # Run the ISMN export_geojson command
      ismn export_geojson "${dir}" -f network -f station -f depth -f timerange -f frm_class -var soil_moisture
      chown 100000:100033 ismn_sensors.json
      chmod 775 ismn_sensors.json
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
  psql -h qa4sm-db -p 5432 -U postgres -q -c '\set ON_ERROR_STOP on' \
    -c "CREATE DATABASE $QA4SM_DB_NAME;" \
    -c "CREATE USER $QA4SM_DB_USER WITH ENCRYPTED PASSWORD '$QA4SM_DB_PASSWORD';" \
    -c "GRANT ALL PRIVILEGES ON DATABASE $QA4SM_DB_NAME TO $QA4SM_DB_USER;"

  psql -h qa4sm-db -p 5432 -U postgres -q -d $QA4SM_DB_NAME -c '\set ON_ERROR_STOP on' \
    -c "GRANT USAGE, CREATE ON SCHEMA public TO $QA4SM_DB_USER;"
	echo "DB has been created."
  NEW_DB="TRUE"
fi

# Check if DB_UPDATE is true and upload the dump if necessary
if [ "$DB_UPDATE" = "TRUE" ]; then
    echo "Updating DB from dump..."
    if [ -f "/var/lib/postgresql/$DB_DUMP_NAME" ]; then
        psql -h qa4sm-db -p 5432 -U postgres -d $QA4SM_DB_NAME -q -f "/var/lib/postgresql/$DB_DUMP_NAME"
        echo "DB dump uploaded successfully."
    else
        echo "DB dump file not found: /var/lib/postgresql/$DB_DUMP_NAME"
        exit 1
    fi
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
	  python $APP_DIR/manage.py generateautocleanupscript --path /var/lib/qa4sm-web-val/valentina/cronjob-scripts


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

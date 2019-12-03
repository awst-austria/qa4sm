#!/bin/bash
set -e
set -x
APP_DIR="/var/lib/qa4sm-web-val/valentina"
PGPASSWORD="$POSTGRES_PASSWORD"
ADMIN_PASS="12admin34"

. /opt/miniconda/etc/profile.d/conda.sh
conda activate /var/lib/qa4sm-web-val/virtenv
python $APP_DIR/manage.py collectstatic --noinput

echo "Pg password: $PGPASSWORD"

if psql -h qa4sm-db -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw $QA4SM_DB_NAME; then
    echo "DB exists"
else
	echo "DB does not exist, let's create it..."
	psql -h qa4sm-db -p 5432 -U postgres -q -c '\set ON_ERROR_STOP on' -c "CREATE DATABASE $QA4SM_DB_NAME;" -c "CREATE USER $QA4SM_DB_USER WITH ENCRYPTED PASSWORD '$QA4SM_DB_PASSWORD';" -c "GRANT ALL PRIVILEGES ON DATABASE $QA4SM_DB_NAME TO $QA4SM_DB_USER;"
	if psql -h qa4sm-db -p 5432 -U postgres -lqt | cut -d \| -f 1 | grep -qw $QA4SM_DB_NAME; then
		echo "DB has been created, building schema"
		python $APP_DIR/manage.py migrate
		echo "Loading fixtures"
		python $APP_DIR/manage.py loaddata versions
		python $APP_DIR/manage.py loaddata variables
		python $APP_DIR/manage.py loaddata filters
		python $APP_DIR/manage.py loaddata datasets
                echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'qa4sm@awst.at', '$ADMIN_PASS')" | python $APP_DIR/manage.py shell

	else
		echo "DB creation failed"
		exit -1
	fi
fi
ln -s /data/qa4sm/data /var/lib/qa4sm-web-val/valentina/data
exec apachectl -D FOREGROUND


if psql -h qa4sm-db -p 5432 -U postgre -lqt | cut -d \| -f 1 | grep -qw $QA4SM_DB_NAME; then
    echo "DB exists"
else
	echo "DB does not exist, let's create it..."
	psql postgres -q -c '\set ON_ERROR_STOP on' -c "\set db_name '$QA4SM_DB_NAME'" -c "\set db_owner '$QA4SM_DB_USER'" -c "\set db_owner_pass '$QA4SM_DB_PASSWORD'" -f "$SCRIPT_DIR/$SCHEMA_UPGR_SCRIPT"
    # ruh-roh
    # $? is 1
fi

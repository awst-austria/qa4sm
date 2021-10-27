#!/usr/bin/python
import sys
import pathlib
import os.path
from os import path

ws_dir = 'prod'
if len(sys.argv) > 1:
    ws_dir = sys.argv[1]
else:
    print('Missing basepath')
    sys.exit(1)

# webapp folders
webapp_log_dir =  ws_dir + '/webapp/log'
webapp_output_dir = ws_dir + '/webapp/output'
webapp_settings_dir = ws_dir + '/webapp/settings'

# db folders
db_log_dir = ws_dir + '/db/log'
db_data_dir =  ws_dir + '/db/data'

# celery worker folders
celery_log_dir = ws_dir + '/celery-w1/log'

if not path.exists(webapp_log_dir):
    print('Creating folder: {}'.format(webapp_log_dir))
    pathlib.Path(webapp_log_dir).mkdir(parents=True, exist_ok=True)

if not path.exists(webapp_output_dir):
    print('Creating folder: {}'.format(webapp_output_dir))
    pathlib.Path(webapp_output_dir).mkdir(parents=True, exist_ok=True)

if not path.exists(webapp_settings_dir):
    print('Creating folder: {}'.format(webapp_settings_dir))
    pathlib.Path(webapp_settings_dir).mkdir(parents=True, exist_ok=True)

if not path.exists(db_log_dir):
    print('Creating folder: {}'.format(db_log_dir))
    pathlib.Path(db_log_dir).mkdir(parents=True, exist_ok=True)

if not path.exists(db_data_dir):
    print('Creating folder: {}'.format(db_data_dir))
    pathlib.Path(db_data_dir).mkdir(parents=True, exist_ok=True)

if not path.exists(celery_log_dir):
    print('Creating folder: {}'.format(celery_log_dir))
    pathlib.Path(celery_log_dir).mkdir(parents=True, exist_ok=True)
    

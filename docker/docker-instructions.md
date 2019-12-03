#Preparation

## Prepare directories on the host
* Database e.g.:	/var/qa4sm/db
* Data e.g.:		/var/qa4sm/data
* Results e.g.:		/var/qa4sm/results

## Adjust mount points in run scripts
* Set the mount points in the run scripts:
- db/run.sh
- webapp/run.sh
- celery-w/run.sh

# Set the desired QA4SM branch to be built
In `webapp/Dockerfile` and `celery-w/Dockerfile` set the correct git branch to be checked out for build.
Replace "dockerize" with the desired branch or tag in the following line:
`RUN git clone -b dockerize --single-branch https://github.com/awst-austria/qa4sm.git /tmp/qa4sm-git`


## Set password for the email account
Set the `EMAIL_HOST_PASSWORD` in webapp/settings_conf.py

## Build the required containers
* webapp/build.sh
* celery-w/build.sh

## Start containers
* db/run.sh
* rabbitmq/run.sh
* redis/run.sh
* webapp/run.sh
* celery-w/run.sh

## Webapp default admin account
* Defined in webapp/entrypoint.sh
* username: admin
* password: 12admin34
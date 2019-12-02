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

## Build the required containers
* webapp/build.sh
* celery-w/build.sh

## Start containers
* [container name]/run.sh

## Webapp default admin account
* Defined in webapp/entrypoint.sh
* username: admin
* password: 12admin34
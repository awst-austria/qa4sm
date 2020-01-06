#!/bin/bash
#-dit
docker run -dit --rm --env-file ../webapp.env --network qa4sm-net \
--name qa4sm-celery \
--hostname qa4sm-celery \
--mount type=bind,source=/awst/projects/QA4SM/data,target=/data/qa4sm/data awst/qa4sm-celery:1.0

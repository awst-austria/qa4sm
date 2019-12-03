#!/bin/bash
docker run -dit --rm --env-file ../webapp.env --network qa4sm-net --name qa4sm-webapp --hostname qa4sm-webapp \
--mount type=bind,source=/awst/projects/QA4SM/data,target=/data/qa4sm/data \
--mount type=bind,source=/awst/projects/QA4SM/output,target=/var/lib/qa4sm-web-val/valentina/output -p 8080:80 awst/qa4sm-webapp:1.0

#!/bin/bash
docker run -dit --rm --env-file ../webapp.env --mount type=bind,source=/var/qa4sm/db,target=/var/lib/postgresql/data \
--network qa4sm-net --name qa4sm-db --hostname qa4sm-db postgres


#!/bin/bash
docker run -dit --rm --network qa4sm-net --name qa4sm-redis --hostname qa4sm-redis redis

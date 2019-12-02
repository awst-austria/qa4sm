#!/bin/bash
docker run -dit --rm --network qa4sm-net --name qa4sm-rabbitmq --hostname qa4sm-rabbitmq rabbitmq

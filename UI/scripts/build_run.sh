#!/bin/bash
set -e
npm install
ng build --prod --deploy-url /ui/ --base-href /ui/
cp -r ../dist/UI ../docker/ui
docker stop qa4sm_ui
docker rm qa4sm_ui --force
docker image rm qa4sm_ui
docker build -t qa4sm_ui ../docker
docker run --name qa4sm_ui --restart unless-stopped -d -p 8013:80 qa4sm_ui

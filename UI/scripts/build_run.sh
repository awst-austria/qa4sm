#!/bin/bash
npm install
ng build --prod --deploy-url /ui/ --base-href /ui/
cp -r ../dist/UI ../docker/ui
docker stop qa4sm_ui
docker rm qa4sm_ui --force
docker image rm qa4sm_ui
docker build -t qa4sm_ui ../docker
docker run --rm --name qa4sm_ui -d -p 8013:80 qa4sm_ui

#!/bin/bash
npm install
ng build --prod --deploy-url /ui/ --base-href /ui/
cp ../dist/UI ./ui
docker stop qa4sm_ui
docker rm qa4sm_ui --force
docker image rm qa4sm_ui
docker build -t qa4sm_ui
docker run --name qa4sm_ui qa4sm_ui -p 8013:80 -d

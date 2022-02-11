#!/bin/bash
set -e
npm install
ng build --prod --deploy-url / --base-href /
cp -r ../dist/UI ../docker/ui
docker build -t qa4sm_ui ../docker

#!/bin/bash
set -e
docker run --name qa4sm_ui --restart unless-stopped -d -p 8013:80 qa4sm_ui

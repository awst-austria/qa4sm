#!/bin/bash
set -e
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
npm install
ng build --prod --deploy-url / --base-href /
cp -r dist/UI docker/ui

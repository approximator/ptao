#!/bin/bash

set -eu

cd $GITHUB_WORKSPACE
ls -lah

cd ./apms-ui

npm install --production
npm run build

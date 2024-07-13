#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

"${BASE_DIR}/set-version.sh"

docker build --progress plain --pull --tag "${DOCKER_NAME}:latest" .

# Restore 'develop' version
"${BASE_DIR}/set-version.sh" develop

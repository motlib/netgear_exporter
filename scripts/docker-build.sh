#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

"${BASE_DIR}/set-version.sh"

DOCKER_BUILD_OPTS="${DOCKER_BUILD_OPTS} \
    --progress plain \
    --pull"

docker build \
    ${DOCKER_BUILD_OPTS} \
    --tag "${DOCKER_NAME}:latest" \
    .

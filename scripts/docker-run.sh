#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

"${BASE_DIR}/docker-build.sh"

DOCKER_OPTS="--rm --interactive --tty ${DOCKER_PUBLISH}"

docker run ${DOCKER_OPTS} "${DOCKER_NAME}:latest"

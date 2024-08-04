#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

log_info "Going to upload docker image '${DOCKER_NAME}' to '${HOST}'."

docker image ls "${DOCKER_NAME}"

echo

docker save "${DOCKER_NAME}" | pv | pbzip2 | ssh "${DOCKER_DEPLOY_HOST}" docker load

ssh "${DOCKER_DEPLOY_HOST}" 'cd /data/docker/topy && docker-compose up -d'

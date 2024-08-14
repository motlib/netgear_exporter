#!/usr/bin/bash

MODULES="promexp netgear_exporter"

METADATA_FILE=netgear_exporter/metadata.py

DOCKER_NAME="motlib/netgear_exporter"

DOCKER_PUBLISH="-p 8000:8000"

DOCKER_DEPLOY_HOST="npi3"

DO_PYLINT=yes
DO_PYTEST=yes
DO_MYPY=yes
DO_FORMAT=yes

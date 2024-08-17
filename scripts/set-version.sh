#!/bin/bash

source "$(dirname $0)/lib/frame.sh"

METADATA_FILE=pyproject.toml

# If a first parameter is given, take it as a version. Otherwise use the
# git version.
if [ -z "${VERSION}" ]; then
    VERSION=$(git describe --exact-match 2> /dev/null || true)
    if [ -z "${VERSION}" ]; then
        VERSION="$(git describe --tags | cut -d '-' -f 1).dev+$(git rev-parse --short HEAD)"
    fi
fi

sed -r -i -e "s/^version = \".*\"$/version = \"${VERSION}\"/" ${METADATA_FILE}
echo "INFO: Setting version to '${VERSION}' in '${METADATA_FILE}'."

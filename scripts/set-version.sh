#!/bin/bash

source "$(dirname $0)/lib/frame.sh"

if [ ! -f "${METADATA_FILE}" ]; then
    echo "ERROR: Metadata file '${METADATA_FILE}' not found!"
    exit 1
fi

# If a first parameter is given, take it as a version. Otherwise use the
# git version.
if [ -z "$1" ]; then
    VERSION=$(git describe --always)
else
    VERSION=$1
fi

echo "INFO: Setting version to '${VERSION}' in '${METADATA_FILE}'."

sed -r -i -e "s/^VERSION\\s*=\\s*(\".*\"|'.*')$/VERSION = \"${VERSION}\"/" ${METADATA_FILE}

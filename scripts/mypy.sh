#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

in_venv mypy \
       ${MODULES}

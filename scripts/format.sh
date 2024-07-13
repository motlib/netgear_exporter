#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

if [ "$1" == "check" ]; then
    CHECK_MODE="--check"
    log_info "Running code formatter in check mode"
    shift
fi

# Allow to override modules from settings
if [ "$*" != "" ]
then
    MODULES="$*"
fi

in_venv isort --profile black "${CHECK_MODE}" ${MODULES}
in_venv black "${CHECK_MODE}" ${MODULES}

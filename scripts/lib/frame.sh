#!/bin/bash

set -e

BASE_DIR=$(dirname "$0")
LIB_DIR=${BASE_DIR}/lib

source "${LIB_DIR}/colors.sh"

if [[ -z "${EXEC_LEVEL}" ]]; then
    export EXEC_LEVEL=0
else
    export EXEC_LEVEL=$((EXEC_LEVEL+1))
fi

# If necessery prepend the command with a venv entry command
function in_venv {
    ARGS=$*
    if ! grep '.venv' "$(which python)" > /dev/null; then
        PREFIX="pipenv run "
    fi

    ${PREFIX} ${ARGS}
}

# Callback function to run on exit
function the_end {
    RC=$?
    if [ "${RC}" -ne 0 ]; then
        log_error "Failed to execute '$0' - exit code ${RC}"
    else
        log_info "Successfully executed '$0'in ${SECONDS}s"
    fi

    exit ${RC}
}

trap the_end EXIT

# Source settings
source "./settings.sh"

log_info "Starting '$0'"

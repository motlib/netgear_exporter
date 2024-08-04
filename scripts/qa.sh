#!/bin/bash

source "$(dirname "$0")/lib/frame.sh"

function run_if {
    FLAG=$1
    shift
    CMD=$*

    if [ "${!FLAG}" == "yes" ]; then
        ${CMD}
    else
        log_info "Flag '${FLAG}' is disabled"
    fi
}

#[ "${DO_FORMAT}" == "no" ] || "${BASE_DIR}/format.sh" check
run_if DO_FORMAT "${BASE_DIR}/format.sh" check

run_if DO_PYLINT "${BASE_DIR}/pylint.sh"

run_if DO_MYPY "${BASE_DIR}/mypy.sh"

run_if DO_PYTEST "${BASE_DIR}/pytest.sh"

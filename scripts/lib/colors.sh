#!/bin/bash

# Ansi Escape codes for colored text output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Print an "info" level log message
function log_info {
    echo -e "[${EXEC_LEVEL}] ${GREEN}INFO${NC}: $1"
}

# Print an "error" level log message
function log_error {
    echo -e "[${EXEC_LEVEL}] ${RED}ERROR${NC}: $1"
}

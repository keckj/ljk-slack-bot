#!/bin/bash
set -feu -o pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export SLACK_APP_TOKEN=''
export SLACK_BOT_TOKEN=''

PYTHON_BIN="/usr/bin/python3"
PYTHON_SCRIPT="${SCRIPT_DIR}/app.py"

${PYTHON_BIN} ${PYTHON_SCRIPT}

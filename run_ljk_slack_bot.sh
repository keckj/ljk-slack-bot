#!/bin/bash
set -feu -o pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

export SLACK_APP_TOKEN='xapp-1-A065FK9S9PV-6185809785410-cb37dbae71402c9f3633a60d1f53366e2ba2b262339c4b03928550d0868bb20a'
export SLACK_BOT_TOKEN='xoxb-6164000779191-6185759966434-UF8BdZuOzwofBijJEr2gh0ga'

PYTHON_BIN="/usr/bin/python3"
PYTHON_SCRIPT="${SCRIPT_DIR}/app.py"

${PYTHON_BIN} ${PYTHON_SCRIPT}

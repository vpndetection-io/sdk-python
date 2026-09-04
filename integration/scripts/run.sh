#!/bin/bash

# The integration suite in docker, for a box whose python has no way to build a
# virtualenv or reach PyPI. CI runs `python3 scripts/run.py` directly; this is
# the same entry point with an interpreter around it.
#
#   ./scripts/run.sh
#
# The four tier keys are read from the environment and passed through by NAME, so
# no key ever reaches a command line. Only the integration directory is mounted:
# the suite must see the published package rather than the source beside it.

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.13-slim}"

docker run --rm \
    -v "$PWD:/app" -w /app \
    -e PIP_ROOT_USER_ACTION=ignore \
    -e VPNDETECTION_STAGING_KEY_FREE \
    -e VPNDETECTION_STAGING_KEY_STARTER \
    -e VPNDETECTION_STAGING_KEY_SCALE \
    -e VPNDETECTION_STAGING_KEY_MAX \
    "$PYTHON_IMAGE" python3 scripts/run.py "$@"

#!/bin/bash

# Publishes the package to PyPI from inside the official Python image, so a
# release needs nothing installed locally beyond docker and works identically on
# any machine. The release workflow does the same steps on a tag; this is the
# manual path for a first release or when Actions is not an option.
#
#   PYPI_TOKEN=... ./scripts/publish.sh            # publish
#   DRY_RUN=1 ./scripts/publish.sh                 # build + check, upload nothing
#
# A token is only needed for the FIRST publish: PyPI configures trusted
# publishing against an EXISTING project, so there is nothing to attach an OIDC
# publisher to until the name is taken. Once release.yml has published once with
# a trusted publisher configured, the token can be deleted.
#
# The dist/ directory is an anonymous volume so a build inside the container
# cannot leave root-owned artifacts in the working tree.

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.13-slim}"
DRY_RUN="${DRY_RUN:-}"

if [ -z "$DRY_RUN" ] ; then
    : "${PYPI_TOKEN:?set PYPI_TOKEN to a PyPI API token, or set DRY_RUN=1 to rehearse}"
    upload="twine upload dist/*"
else
    PYPI_TOKEN=""
    upload="echo 'DRY_RUN: built and checked, uploading nothing'"
fi

docker run --rm \
    -v "$PWD:/w" -v /w/dist \
    -w /w \
    -e TWINE_USERNAME=__token__ \
    -e TWINE_PASSWORD="$PYPI_TOKEN" \
    -e PIP_ROOT_USER_ACTION=ignore \
    "$PYTHON_IMAGE" sh -euc "
        pip install --quiet --upgrade pip build twine
        pip install --quiet -e '.[dev]'
        pytest -q
        python -m build
        twine check dist/*
        $upload
    "

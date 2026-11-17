#!/bin/bash

# Regenerates src/vpndetection/_generated/ from the PINNED spec in this repo.
#
# Unlike most of the SDKs, the generated client is COMMITTED here: a Python
# package is installed from source, so a gitignored generated tree would mean a
# `pip install` of this repo produced a package that cannot import itself.
# Refresh it deliberately and commit the diff alongside any spec change.
#
# The generator lives in a throwaway virtualenv under /tmp rather than in the
# working tree, because a venv is thousands of files and one committed by
# accident is far more annoying to remove than to recreate.
#
#   ./scripts/generate.sh

set -euo pipefail

cd "$(dirname "$0")/.."

VENV="${VENV:-/tmp/vpndetection-sdk-python-codegen}"
GENERATOR_VERSION="${GENERATOR_VERSION:-0.29.1}"

if [ ! -x "$VENV/bin/openapi-python-client" ] ; then
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --upgrade pip
    "$VENV/bin/pip" install --quiet "openapi-python-client==${GENERATOR_VERSION}"
fi

# ruff must be on PATH: the generator shells out to it to format and lint its
# own output, and silently skips both when it cannot find it. It picks up this
# repo's pyproject.toml, so `requires-python` decides whether the models import
# `Self` from typing or from typing_extensions - which is the difference between
# three runtime dependencies and four.
export PATH="$VENV/bin:$PATH"

rm -rf src/vpndetection/_generated
openapi-python-client generate \
    --path spec/openapi.yaml \
    --meta none \
    --output-path src/vpndetection/_generated

# The generator's own docstring templates carry em-dashes, which this codebase does
# not use anywhere. Normalizing them here keeps generation deterministic.
find src/vpndetection/_generated -name '*.py' -exec sed -i 's/\xe2\x80\x94/ - /g' {} +

# A value the API adds to a closed vocabulary in an ANSWER comes back as served rather
# than failing the whole call, so a release already installed keeps reading the API's
# answers. Each response enum gains a `_missing_` returning a member that carries the
# value. A wrong type is still refused, a request still refuses a value outside the
# pinned list before the network (`wire_format`), and a listed file the generator stops
# emitting stops this script rather than leaving one enum closed.
for enum in entitlement_plan_tier standing database_format download_outcome \
    database_license_type_type_1 database_license_type_type_2_type_1 \
    database_license_type_type_3_type_1 ; do
    file="src/vpndetection/_generated/models/${enum}.py"
    [ -f "$file" ] || { echo "no ${file}: the generated enums moved" >&2 ; exit 1 ; }
    class="$(sed -n 's/^class \([A-Za-z0-9]*\)(StrEnum):$/\1/p' "$file")"
    [ -n "$class" ] || { echo "${file} holds no StrEnum" >&2 ; exit 1 ; }
    cat >> "$file" <<EOF

    @classmethod
    def _missing_(cls, value: object) -> "${class} | None":
        # A value the API added after this release, handed back as served.
        if not isinstance(value, str):
            return None
        member = str.__new__(cls, value)
        member._name_ = value
        member._value_ = value
        return member
EOF
done

echo "src/vpndetection/_generated <- spec/openapi.yaml"
grep -m1 '^  version:' spec/openapi.yaml

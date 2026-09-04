"""The gate and the run banner.

The gate runs before collection rather than as a test, because a suite pointed at local
source is not failing, it is answering the wrong question, and every test in it would pass
while doing so.
"""

from __future__ import annotations

import pytest
import tiers
from staging import assert_published_artifact, notice


def pytest_configure(config: pytest.Config) -> None:
    assert_published_artifact()

    with_key = [rung.tier for rung in tiers.observable()]
    absent = [rung.tier for rung in tiers.RUNGS if rung.skip_reason() is not None]
    print(f"==> tiers with a key: {', '.join(with_key)}")
    if absent:
        notice(f"no staging key for {', '.join(absent)}: those tiers are skipped")

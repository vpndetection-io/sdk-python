"""Fixtures. The test doubles themselves live in helpers.py."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from helpers import ClientFactory


@pytest.fixture(params=["sync", "async"])
def make_client(request: pytest.FixtureRequest) -> Iterator[ClientFactory]:
    """A factory for clients of whichever flavor this run is exercising."""
    factory = ClientFactory(request.param)
    yield factory
    factory.close_all()

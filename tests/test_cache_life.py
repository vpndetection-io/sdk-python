"""A spent trial's or a reached cap's answer ends with a renewed trial or a raised cap, so it
is cached for a minute at most rather than for the client's TTL."""

from __future__ import annotations

from typing import Any

import pytest
from helpers import ClientFactory, Stub

from vpndetection._core import Cache

FLAGS: dict[str, dict[str, Any]] = {
    "45.83.91.1": {},
    "45.83.91.2": {"trial_expired": False, "cap_reached": False},
    "45.83.91.3": {"trial_expired": True},
    "45.83.91.4": {"cap_reached": True},
}

CASES = [
    ("45.83.91.1", 3600.0, 3600.0),
    ("45.83.91.2", 3600.0, 3600.0),
    ("45.83.91.3", 3600.0, 60.0),
    ("45.83.91.4", 3600.0, 60.0),
    ("45.83.91.3", 5.0, 5.0),
    ("45.83.91.4", 5.0, 5.0),
    ("45.83.91.1", 5.0, 5.0),
]


class FakeTimer:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def stub() -> Stub:
    return Stub({ip: {"body": {"ip": ip, "is_vpn": False, **flags}} for ip, flags in FLAGS.items()})


@pytest.mark.parametrize("how", ["lookup", "lookup_batch"])
@pytest.mark.parametrize(("ip", "ttl", "want"), CASES)
def test_each_answer_is_cached_as_long_as_its_flags_allow(
    make_client: ClientFactory, how: str, ip: str, ttl: float, want: float
) -> None:
    client = make_client(transport=stub().transport)
    timer = FakeTimer()
    cache = Cache(100, ttl, timer=timer)
    client.client._cache = cache

    if how == "lookup":
        client.lookup(ip)
    else:
        client.lookup_batch([ip, "45.83.91.1"])

    timer.now += want - 0.01
    assert cache.get(ip) is not None, f"{ip} under a {ttl} s TTL went stale early"
    timer.now += 0.02
    assert cache.get(ip) is None, f"{ip} under a {ttl} s TTL outlived {want} s"


def test_a_reduced_answer_is_still_cached_so_a_repeat_sends_nothing(
    make_client: ClientFactory,
) -> None:
    s = stub()
    client = make_client(transport=s.transport)

    client.lookup("45.83.91.3")
    again = client.lookup("45.83.91.3")

    assert again.trial_expired is True
    assert len(s.calls) == 1

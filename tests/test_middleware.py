"""The middleware half of the shared conformance corpus, plus the Python-specific
parts of it.

The corpus is language-neutral JSON and this SDK's `Result` already uses the wire's
own names, so a condition needs no translation here at all - which is itself worth
knowing when a sibling SDK's test file is full of renaming.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import time
from typing import Any

import pytest
from helpers import Stall, Stub

from vpndetection import AsyncVPNDetection, VPNDetection, VPNDetectionError
from vpndetection.middleware import (
    AsyncCore,
    Core,
    Lookup,
    Options,
    RequestView,
    Selectors,
    bind_selectors,
    matches,
    missing_members,
)
from vpndetection.models import Result, to_result

CORPUS = json.loads((pathlib.Path(__file__).parent.parent / "testdata/testdata.json").read_text())
MIDDLEWARE = CORPUS["middleware"]
PUBLIC_IP = "45.83.91.1"


def _result_for(case: dict[str, Any]) -> Result:
    if "bogon" in case:
        # Answered locally, so this needs no transport and pins the synthesized shape
        # rather than a fixture's idea of it.
        return VPNDetection().lookup(case["bogon"])
    return to_result(case["body"])


@pytest.mark.parametrize("case", MIDDLEWARE["conditions"], ids=lambda c: c["name"])
def test_corpus_conditions(case: dict[str, Any]) -> None:
    result = _result_for(case)
    assert matches(case["condition"], result) is case["expect"]["blocked"], case["why"]
    assert sorted(missing_members(case["condition"], result)) == sorted(
        case["expect"]["missing"]
    ), case["why"]


@pytest.mark.parametrize("case", MIDDLEWARE["invalidConditions"], ids=lambda c: c["name"])
def test_corpus_refuses_a_condition_that_constrains_nothing(case: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="constrains nothing"):
        Core(Options(block_condition=case["condition"]), lambda _: PUBLIC_IP)


class Req:
    """The least a framework can offer, so the core is exercised without one."""

    def __init__(self, headers: dict[str, str] | None = None, ip: str = PUBLIC_IP) -> None:
        self.headers = {name.lower(): value for name, value in (headers or {}).items()}
        self.ip = ip


SELECTORS: Selectors[Req] = bind_selectors(
    lambda request: RequestView(
        header=lambda name: request.headers.get(name.lower()),
        framework_ip=lambda: request.ip,
    )
)


def _core(**options: Any) -> Core[Req]:
    return Core(Options(**options), SELECTORS.default)


def _serving(body: dict[str, Any], *, status: int = 200) -> VPNDetection:
    stub = Stub({body.get("ip", PUBLIC_IP): {"body": body, "status": status}})
    return VPNDetection(cache=False, retries=0, transport=stub.transport)


def test_enriches_without_blocking_when_no_condition_is_configured() -> None:
    core = _core(client=_serving({"ip": PUBLIC_IP, "is_vpn": True}))
    lookup = core.evaluate(Req())
    assert lookup is not None
    assert lookup.blocked is False
    assert lookup.result is not None and lookup.result.is_vpn is True
    assert lookup.ip == PUBLIC_IP


def test_skip_claims_the_request() -> None:
    core = _core(client=_serving({"ip": PUBLIC_IP, "is_vpn": True}), skip=lambda _: True)
    assert core.evaluate(Req()) is None


def test_fails_open_on_a_lookup_error_and_closed_only_when_asked() -> None:
    failing = _serving({"ip": PUBLIC_IP, "error": "boom"}, status=500)
    opened = _core(client=failing, block_condition={"is_vpn": True})
    lookup = opened.evaluate(Req())
    assert lookup is not None
    assert lookup.blocked is False
    assert isinstance(lookup.error, VPNDetectionError)
    assert lookup.result is None

    closed = _core(client=failing, block_condition={"is_vpn": True}, fail_closed=True)
    shut = closed.evaluate(Req())
    assert shut is not None and shut.blocked is True


def test_a_private_client_address_warns_once_and_never_reaches_the_network() -> None:
    warnings: list[str] = []
    core = _core(
        client=_serving({"ip": "10.0.0.7", "is_vpn": True}),
        block_condition={"is_vpn": True},
        on_warn=warnings.append,
    )
    for _ in range(2):
        lookup = core.evaluate(Req(ip="10.0.0.7"))
        assert lookup is not None
        assert lookup.blocked is False
        assert lookup.result is not None and lookup.result.is_bogon is True
    assert len(warnings) == 1, "a per-request warning is an outage of its own"
    assert "not a public address" in warnings[0]


def test_a_missing_member_warns_once_or_raises_on_request() -> None:
    free = _serving({"ip": PUBLIC_IP, "is_vpn": True})
    warnings: list[str] = []
    warned = _core(client=free, block_condition={"is_hosting": True}, on_warn=warnings.append)
    assert warned.evaluate(Req()) is not None
    warned.evaluate(Req())
    assert len(warnings) == 1
    assert "is_hosting" in warnings[0]

    strict = _core(client=free, block_condition={"is_hosting": True}, on_missing_field="raise")
    with pytest.raises(ValueError, match="does not include"):
        strict.evaluate(Req())

    def fail(_: str) -> None:
        raise AssertionError("ignore must not warn")

    quiet = _core(
        client=free,
        block_condition={"is_hosting": True},
        on_missing_field="ignore",
        on_warn=fail,
    )
    assert quiet.evaluate(Req()) is not None


def test_selectors_read_what_they_say_they_read() -> None:
    request = Req({"X-Forwarded-For": "203.0.113.9, 70.41.3.18, 150.172.238.178"}, ip="10.0.0.1")
    assert SELECTORS.default(request) == "10.0.0.1"
    assert SELECTORS.xff()(request) == "203.0.113.9"
    assert SELECTORS.xff(1)(request) == "150.172.238.178"
    assert SELECTORS.xff(2)(request) == "70.41.3.18"
    assert SELECTORS.header("CF-Connecting-IP")(request) == "10.0.0.1"

    cloudflared = Req({"CF-Connecting-IP": "198.51.100.4"}, ip="10.0.0.1")
    assert SELECTORS.header("CF-Connecting-IP")(cloudflared) == "198.51.100.4"
    assert SELECTORS.xff()(Req({}, ip="10.0.0.1")) == "10.0.0.1"


def test_an_unresolvable_address_warns_and_does_not_block() -> None:
    warnings: list[str] = []
    core: Core[Req] = Core(
        Options(block_condition={"is_vpn": True}, on_warn=warnings.append),
        lambda _: None,
    )
    lookup = core.evaluate(Req())
    assert lookup is not None
    assert lookup.blocked is False
    assert isinstance(lookup.error, VPNDetectionError)
    assert "could not resolve a client address" in warnings[0]


def test_an_injected_client_is_used_rather_than_a_second_one_built() -> None:
    shared = VPNDetection(
        transport=Stub({PUBLIC_IP: {"body": {"ip": PUBLIC_IP, "is_vpn": True}}}).transport
    )
    core = _core(client=shared)
    assert core.evaluate(Req()) is not None
    # The second call must come from the shared cache, which is only observable
    # because it is the SAME client the caller still holds.
    assert shared.lookup(PUBLIC_IP).is_vpn is True


def test_the_timeout_bounds_a_lookup_through_a_client_passed_in() -> None:
    with Stall() as stall, VPNDetection(base_url=stall.url, timeout=5.0, retries=0) as client:
        core = _core(client=client, timeout=0.2)
        started = time.monotonic()
        lookup = core.evaluate(Req())
        elapsed = time.monotonic() - started

    assert lookup is not None and lookup.blocked is False
    assert isinstance(lookup.error, VPNDetectionError) and lookup.error.kind == "network"
    assert elapsed < 2.5, f"the lookup held the request for {elapsed:.2f}s"


def test_the_timeout_bounds_a_lookup_through_an_async_client_passed_in() -> None:
    async def evaluate(url: str) -> Lookup | None:
        async with AsyncVPNDetection(base_url=url, timeout=5.0, retries=0) as client:
            core: AsyncCore[Req] = AsyncCore(Options(client=client, timeout=0.2), SELECTORS.default)
            return await core.evaluate(Req())

    with Stall() as stall:
        started = time.monotonic()
        lookup = asyncio.run(evaluate(stall.url))
        elapsed = time.monotonic() - started

    assert lookup is not None and lookup.blocked is False
    assert isinstance(lookup.error, VPNDetectionError) and lookup.error.kind == "network"
    assert elapsed < 2.5, f"the lookup held the request for {elapsed:.2f}s"


def test_an_async_client_is_refused_by_the_sync_core() -> None:
    with pytest.raises(TypeError, match="use AsyncCore"):
        Core(Options(client=AsyncVPNDetection()), SELECTORS.default)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), "30", True])
def test_a_timeout_no_lookup_can_meet_is_refused_when_the_middleware_is_built(
    timeout: Any,
) -> None:
    """Otherwise every lookup fails, and the middleware fails open on every request."""
    with pytest.raises(ValueError, match="timeout"):
        Core(Options(timeout=timeout), SELECTORS.default)
    with pytest.raises(ValueError, match="timeout"):
        AsyncCore(Options(timeout=timeout), SELECTORS.default)

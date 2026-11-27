"""The middleware half of the shared conformance corpus, plus the Python-specific
parts of it.

The corpus is language-neutral JSON and this SDK's `Result` already uses the wire's
own names, so a condition needs no translation here at all - which is itself worth
knowing when a sibling SDK's test file is full of renaming.
"""

from __future__ import annotations

import asyncio
import dataclasses
import http.server
import json
import pathlib
import threading
import time
from typing import Any, Self

import pytest
from helpers import Stall, Stub

from vpndetection import AsyncVPNDetection, VPNDetection, VPNDetectionError
from vpndetection.middleware import (
    AsyncCore,
    Core,
    Guard,
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


BOT = {
    "provider": "google",
    "provider_name": "Google",
    "agents": ["GoogleOther", "Googlebot"],
    "categories": ["other", "search_engine"],
    "verified": True,
    "identity": "verified",
    "verified_by": "list",
    "confidence": "high",
    "first_seen": "2026-11-21",
    "last_seen": "2026-11-21",
}


@pytest.mark.parametrize("condition", [{"is_bot": True}, {"bot": {"verified": True}}])
def test_a_condition_on_a_bot_blocks_a_served_bot_and_passes_the_rest(
    condition: dict[str, Any],
) -> None:
    for is_bot, bot in ((True, BOT), (False, {})):
        body = {"ip": PUBLIC_IP, "is_vpn": False, "is_bot": is_bot, "bot": bot}
        lookup = _core(client=_serving(body), block_condition=condition).evaluate(Req())
        assert lookup is not None and lookup.error is None, lookup
        assert lookup.result is not None and lookup.result.is_bot is is_bot
        assert lookup.blocked is is_bot, f"{condition} against is_bot {is_bot}"


def test_a_condition_inside_a_member_held_as_a_list_matches_any_element() -> None:
    body = {"ip": PUBLIC_IP, "is_vpn": False, "is_bot": True, "bot": BOT}
    for condition, blocked in (
        ({"bot": {"agents": "googlebot"}}, True),
        ({"bot": {"agents": ["Bingbot", "Googlebot"]}}, True),
        ({"bot": {"categories": "search_engine"}}, True),
        ({"bot": {"agents": "Bingbot"}}, False),
        ({"bot": {"agents": ["Bingbot", "DuckDuckBot"]}}, False),
    ):
        lookup = _core(client=_serving(body), block_condition=condition).evaluate(Req())
        assert lookup is not None and lookup.result is not None
        assert lookup.blocked is blocked, condition


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


# A keyless answer carries the AS without its `type`, a paid plan's member, which the type reads
# as the empty string. The core knows the answer left it out, so a condition on it never matches
# and is reported by its path, and the empty string is never taken for a value.
ASN_ANSWER = {
    "asn": 9009,
    "name": "M247 Europe SRL",
    "domain": "m247global.com",
    "prefix": "146.70.116.0/24",
    "country": "US",
    "rpki_status": "valid",
}
UNLIMITED_BODY = {"ip": PUBLIC_IP, "is_vpn": True, "asn": ASN_ANSWER}
PAID_BODY = {"ip": PUBLIC_IP, "is_vpn": True, "asn": {**ASN_ANSWER, "type": "hosting"}}


@pytest.mark.parametrize(
    "condition",
    [
        {"asn": {"type": "hosting"}},
        {"asn": {"type": ["hosting", ""]}},
        {"asn": {"type": ""}},
        [{"is_hosting": True}, {"asn": {"type": "hosting"}}],
    ],
    ids=["a value", "any-of with the empty one", "the empty one", "one of two"],
)
def test_a_condition_on_the_asn_type_never_matches_an_answer_that_lacks_it(
    condition: Any,
) -> None:
    warnings: list[str] = []
    core = _core(
        client=_serving(UNLIMITED_BODY), block_condition=condition, on_warn=warnings.append
    )

    lookup = core.evaluate(Req())

    assert lookup is not None and lookup.error is None
    assert lookup.result is not None and lookup.result.asn is not None
    assert lookup.result.asn.name == "M247 Europe SRL", "the answer is attached, read"
    assert lookup.blocked is False
    assert len(warnings) == 1
    named = warnings[0].removeprefix("block_condition names ").split(" which ")[0]
    assert named.rstrip(", ").split(", ")[-1] == "asn.type", "reported by its path, not as `asn`"
    assert "asn" not in named.replace("asn.type", "").split(", ")


def test_the_same_condition_blocks_an_answer_that_carries_the_type() -> None:
    warnings: list[str] = []
    for condition, blocked in (
        ({"asn": {"type": "hosting"}}, True),
        ({"asn": {"type": ["isp", "hosting"]}}, True),
        ({"asn": {"type": "isp"}}, False),
    ):
        core = _core(client=_serving(PAID_BODY), block_condition=condition, on_warn=warnings.append)
        lookup = core.evaluate(Req())
        assert lookup is not None and lookup.result is not None
        assert lookup.result.asn is not None and lookup.result.asn.type == "hosting"
        assert lookup.blocked is blocked, condition
    assert warnings == [], "a served type is no plan gap"


def test_a_condition_on_the_asn_type_raises_on_request_and_can_be_silenced() -> None:
    strict = _core(
        client=_serving(UNLIMITED_BODY),
        block_condition={"asn": {"type": "hosting"}},
        on_missing_field="raise",
    )
    with pytest.raises(ValueError, match="asn.type"):
        strict.evaluate(Req())

    def fail(_: str) -> None:
        raise AssertionError("ignore must not warn")

    quiet = _core(
        client=_serving(UNLIMITED_BODY),
        block_condition={"asn": {"type": "hosting"}},
        on_missing_field="ignore",
        on_warn=fail,
    )
    lookup = quiet.evaluate(Req())
    assert lookup is not None and lookup.blocked is False


def test_a_cached_answer_still_knows_the_asn_type_was_left_out() -> None:
    stub = Stub({PUBLIC_IP: {"body": UNLIMITED_BODY}})
    client = VPNDetection(retries=0, transport=stub.transport)
    warnings: list[str] = []
    core = _core(client=client, block_condition={"asn": {"type": ""}}, on_warn=warnings.append)

    first = core.evaluate(Req())
    second = core.evaluate(Req())

    assert len(stub.calls) == 1, "the second lookup was the cache's"
    for lookup in (first, second):
        assert lookup is not None and lookup.blocked is False
    assert len(warnings) == 1, "warned once, as for any member the plan lacks"
    assert "asn.type" in warnings[0]


def test_the_async_core_reads_the_asn_type_as_left_out_too() -> None:
    async def evaluate() -> tuple[Lookup | None, list[str]]:
        warnings: list[str] = []
        stub = Stub({PUBLIC_IP: {"body": UNLIMITED_BODY}})
        async with AsyncVPNDetection(cache=False, retries=0, transport=stub.transport) as client:
            core: AsyncCore[Req] = AsyncCore(
                Options(
                    client=client,
                    block_condition={"asn": {"type": ""}},
                    on_warn=warnings.append,
                ),
                SELECTORS.default,
            )
            return await core.evaluate(Req()), warnings

    lookup, warnings = asyncio.run(evaluate())

    assert lookup is not None and lookup.blocked is False
    assert lookup.result is not None and lookup.result.asn is not None
    assert len(warnings) == 1 and warnings[0].startswith("block_condition names asn.type,")


def test_a_type_built_by_hand_is_a_value_whatever_the_answer_it_replaces_carried() -> None:
    result = to_result(UNLIMITED_BODY)
    assert result.asn is not None
    assert missing_members({"asn": {"type": "hosting"}}, result) == ["asn.type"]
    assert matches({"asn": {"type": "hosting"}}, result) is False

    built = dataclasses.replace(result, asn=dataclasses.replace(result.asn, type="hosting"))
    assert missing_members({"asn": {"type": "hosting"}}, built) == []
    assert matches({"asn": {"type": "hosting"}}, built) is True

    bare = Result(ip=PUBLIC_IP, is_vpn=True, asn=result.asn)
    assert missing_members({"asn": {"type": "hosting"}}, bare) == []


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


class _KeyServer:
    """A local API that answers every lookup and records the Authorization each one carried."""

    def __init__(self) -> None:
        self.authorizations: list[str | None] = []
        recorded = self.authorizations

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                recorded.append(self.headers.get("Authorization"))
                body = json.dumps({"ip": PUBLIC_IP, "is_vpn": True}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_: Any) -> None:
                pass

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self._server.server_address[1]}"

    def __enter__(self) -> Self:
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_: object) -> None:
        self._server.shutdown()
        self._server.server_close()


@pytest.mark.parametrize("flavor", ["sync", "async"])
def test_a_core_built_from_a_key_sends_that_key(flavor: str) -> None:
    """Every other middleware test hands the core a client, so a core that built its own
    without the key it was given passed them all."""
    with _KeyServer() as server:
        options: Options[Req] = Options(api_key="k_middleware", base_url=server.url)
        if flavor == "sync":
            lookup = Core(options, SELECTORS.default).evaluate(Req())
        else:

            async def evaluate() -> Lookup | None:
                return await AsyncCore(options, SELECTORS.default).evaluate(Req())

            lookup = asyncio.run(evaluate())

    assert lookup is not None and lookup.error is None, lookup
    assert lookup.result is not None and lookup.result.is_vpn is True
    assert server.authorizations == ["Bearer k_middleware"]


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


# A per-view check judges the answer the middleware attached, so it must reach the
# same verdict and the same plan-gap warning as the middleware's own condition, without
# a request of its own.
@pytest.mark.parametrize("case", MIDDLEWARE["conditions"], ids=lambda c: c["name"])
def test_corpus_conditions_through_a_guard(case: dict[str, Any]) -> None:
    warnings: list[str] = []
    guard = Guard(case["condition"], on_warn=warnings.append)
    found = Lookup(blocked=False, ip=PUBLIC_IP, result=_result_for(case))
    assert guard.blocks(found) is case["expect"]["blocked"], case["why"]
    assert len(warnings) == (1 if case["expect"]["missing"] else 0), case["why"]
    for member in case["expect"]["missing"]:
        assert member in warnings[0], case["why"]


@pytest.mark.parametrize("case", MIDDLEWARE["invalidConditions"], ids=lambda c: c["name"])
def test_a_guard_refuses_a_condition_that_constrains_nothing(case: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="constrains nothing"):
        Guard(case["condition"])


def test_a_guard_needs_a_condition() -> None:
    with pytest.raises(ValueError, match="needs a condition"):
        Guard(None)  # type: ignore[arg-type]


def test_a_guard_passes_a_failed_lookup_unless_it_fails_closed() -> None:
    failed = Lookup(blocked=False, ip=PUBLIC_IP, error=VPNDetectionError("network", "down"))
    assert Guard({"is_vpn": True}).blocks(failed) is False
    assert Guard({"is_vpn": True}, fail_closed=True).blocks(failed) is True


def test_a_guard_warns_once_by_its_name_or_raises() -> None:
    found = Lookup(blocked=False, ip=PUBLIC_IP, result=to_result({"ip": PUBLIC_IP, "is_vpn": True}))
    warnings: list[str] = []
    guard = Guard({"is_hosting": True}, on_warn=warnings.append, name="block_if on checkout")
    assert guard.blocks(found) is False
    assert guard.blocks(found) is False
    assert len(warnings) == 1
    assert warnings[0].startswith("block_if on checkout names is_hosting")

    with pytest.raises(ValueError, match="does not include"):
        Guard({"is_hosting": True}, on_missing_field="raise").blocks(found)

    def fail(_: str) -> None:
        raise AssertionError("ignore must not warn")

    quiet = Guard({"is_hosting": True}, on_missing_field="ignore", on_warn=fail)
    assert quiet.blocks(found) is False


def test_a_guard_warns_through_the_logger_by_default(caplog: pytest.LogCaptureFixture) -> None:
    found = Lookup(blocked=False, ip=PUBLIC_IP, result=to_result({"ip": PUBLIC_IP, "is_vpn": True}))
    with caplog.at_level("WARNING", logger="vpndetection"):
        Guard({"is_hosting": True}).blocks(found)
    assert ["block condition names is_hosting" in r.message for r in caplog.records] == [True]

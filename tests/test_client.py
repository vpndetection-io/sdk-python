"""The Python-specific API surface, as distinct from the shared conformance corpus."""

from __future__ import annotations

import asyncio
import dataclasses
import inspect
import time
from collections.abc import Callable
from typing import Any

import attrs
import httpx
import pytest
from helpers import (
    TESTDATA,
    ClientAdapter,
    ClientFactory,
    FakeClock,
    LoopBound,
    Meter,
    SlowBody,
    Stub,
    settle,
)

from vpndetection import (
    DATABASE_FORMATS,
    LICENSE_TYPES,
    STANDINGS,
    AsyncVPNDetection,
    ClassDetail,
    DeviceAuthorization,
    OauthMetadata,
    ProxyDetail,
    Result,
    TokenResponse,
    VpnDetail,
    VPNDetection,
    VPNDetectionError,
    is_bogon,
)
from vpndetection._generated.models.class_detail import ClassDetail as WireClassDetail
from vpndetection._generated.models.database_format import DatabaseFormat
from vpndetection._generated.models.database_license_type_type_1 import DatabaseLicenseTypeType1
from vpndetection._generated.models.database_license_type_type_2_type_1 import (
    DatabaseLicenseTypeType2Type1,
)
from vpndetection._generated.models.database_license_type_type_3_type_1 import (
    DatabaseLicenseTypeType3Type1,
)
from vpndetection._generated.models.device_authorization import (
    DeviceAuthorization as WireDeviceAuthorization,
)
from vpndetection._generated.models.lookup_response import LookupResponse as WireLookupResponse
from vpndetection._generated.models.oauth_metadata import OauthMetadata as WireOauthMetadata
from vpndetection._generated.models.proxy_detail import ProxyDetail as WireProxyDetail
from vpndetection._generated.models.standing import Standing
from vpndetection._generated.models.token_response import TokenResponse as WireTokenResponse
from vpndetection._generated.models.vpn_detail import VpnDetail as WireVpnDetail

# Enough addresses for seven chunks of the batch endpoint's 1000, so a concurrency bound
# has something to bound: one request per chunk, and only the chunks overlap.
ADDRESSES = [f"9.{1 + n // 65536}.{n // 256 % 256}.{n % 256}" for n in range(6001)]

# The client's bound sits far above the call's, so an override accepted and ignored fails on
# how long the call took rather than passing on the timeout it hit anyway.
CLIENT_TIMEOUT = 0.6
CALL_TIMEOUT = 0.1

# A byte this often resets httpx's own per-read timeout for good, so only a deadline over the
# whole attempt ends the call.
TRICKLE = 0.02

DEVICE = DeviceAuthorization(
    device_code="mo_dc_x",
    user_code="BCDF-GHJK",
    verification_uri="https://app.example.test/device",
    expires_in=900,
    interval=5,
)

# Every call that takes a per-call timeout, called with the keyword arguments given.
PER_CALL_TIMEOUT: dict[str, Callable[..., Any]] = {
    "lookup": lambda client, **kw: client.lookup("9.9.9.9", **kw),
    "my_ip": lambda client, **kw: client.my_ip(**kw),
    "my_entitlement": lambda client, **kw: client.my_entitlement(**kw),
    "lookup_batch": lambda client, **kw: _raised(client.lookup_batch(["9.9.9.9"], **kw)["9.9.9.9"]),
    "oauth.metadata": lambda client, **kw: client.oauth.metadata(**kw),
    "oauth.device_authorization": lambda client, **kw: client.oauth.device_authorization(
        "your-client-id", **kw
    ),
    "oauth.exchange_device_code": lambda client, **kw: client.oauth.exchange_device_code(
        "your-client-id", "mo_dc_x", **kw
    ),
    "oauth.exchange_refresh_token": lambda client, **kw: client.oauth.exchange_refresh_token(
        "your-client-id", "mo_rt_x", **kw
    ),
    "oauth.revoke": lambda client, **kw: client.oauth.revoke("your-client-id", "mo_rt_x", **kw),
    "oauth.poll_device_token": lambda client, **kw: client.oauth.poll_device_token(
        "your-client-id", DEVICE, **kw
    ),
}

# The JSON database calls take no per-call options, so the client's bound is theirs.
CLIENT_TIMEOUT_ONLY: dict[str, Callable[[ClientAdapter], Any]] = {
    "database.list": lambda client: client.database.list(),
    "database.download_url": lambda client: client.database.download_url("cdn_ip_v1", "mmdb"),
}


def test_is_bogon_is_on_the_client_and_agrees_with_the_standalone_export(
    make_client: ClientFactory,
) -> None:
    client = make_client()
    for case in TESTDATA["isBogon"]:
        assert client.is_bogon(case["ip"]) is case["expect"], f"{case['ip']} ({case['why']})"
        assert client.is_bogon(case["ip"]) is is_bogon(case["ip"]), (
            f"{case['ip']}: client and export disagree"
        )


def test_a_bogon_lookup_issues_zero_http_requests(make_client: ClientFactory) -> None:
    stub = Stub({})
    client = make_client(transport=stub.transport)
    for ip in ("10.0.0.1", "127.0.0.1", "::1", "fe80::1", "192.168.1.1"):
        assert client.lookup(ip).is_bogon is True
    assert stub.calls == []


def test_batch_concurrency_is_configurable_per_call(make_client: ClientFactory) -> None:
    meter = Meter(make_client.kind)
    client = make_client(transport=meter.transport, cache=False)

    client.lookup_batch(ADDRESSES, concurrency=3)

    assert meter.calls == 7, "one request per chunk of 1000"
    assert meter.peak <= 3, f"peak in flight was {meter.peak}, expected at most 3"
    assert meter.peak > 1, "requests should still overlap"


def test_a_per_call_concurrency_overrides_the_client_default(make_client: ClientFactory) -> None:
    meter = Meter(make_client.kind)
    # Instance default of 2, raised to 6 for this one batch.
    client = make_client(transport=meter.transport, cache=False, concurrency=2)

    client.lookup_batch(ADDRESSES, concurrency=6)

    assert meter.peak > 2, f"override ignored: peak was {meter.peak}, expected above 2"
    assert meter.peak <= 6, f"peak in flight was {meter.peak}, expected at most 6"


def test_without_an_override_the_client_concurrency_still_applies(
    make_client: ClientFactory,
) -> None:
    meter = Meter(make_client.kind)
    client = make_client(transport=meter.transport, cache=False, concurrency=2)

    client.lookup_batch(ADDRESSES)

    assert meter.peak <= 2, f"peak in flight was {meter.peak}, expected at most 2"


@pytest.mark.parametrize("concurrency", [0, -1, 0.5, 1.5, float("nan")])
def test_a_per_call_concurrency_below_one_is_refused_before_any_request(
    make_client: ClientFactory, concurrency: Any
) -> None:
    stub = Stub({})
    client = make_client(transport=stub.transport, cache=False)
    bound = LoopBound()

    outcome = settle(
        lambda: client.lookup_batch(["45.83.91.1", "10.0.0.1"], concurrency=concurrency),
        bound,
        within=5.0,
    )

    assert isinstance(outcome, VPNDetectionError), f"{concurrency}: settled with {outcome!r}"
    assert outcome.kind == "bad_request"
    assert outcome.retryable is False
    assert "concurrency" in str(outcome)
    assert stub.calls == []


def test_retries_are_configurable_per_call(make_client: ClientFactory) -> None:
    stub = Stub({"9.9.9.9": {"status": 500, "body": {"error": "lookup failed"}}})
    client = make_client(transport=stub.transport, cache=False, retries=0)

    with pytest.raises(VPNDetectionError):
        client.lookup("9.9.9.9", retries=2)

    # 1 initial attempt plus 2 retries, rather than the instance's 0.
    assert len(stub.calls) == 3


@pytest.mark.parametrize("call", PER_CALL_TIMEOUT)
def test_a_per_call_timeout_bounds_a_trickling_body_and_leaves_the_clients_own_alone(
    make_client: ClientFactory, call: str
) -> None:
    bound = LoopBound()
    with SlowBody(trickle=TRICKLE) as server:
        client = make_client(base_url=server.url, timeout=CLIENT_TIMEOUT, retries=0)
        client.oauth.use_clock(FakeClock(bound))
        overridden = _timed(lambda: PER_CALL_TIMEOUT[call](client, timeout=CALL_TIMEOUT), bound)
        default = _timed(lambda: PER_CALL_TIMEOUT[call](client), bound)

    assert overridden < CLIENT_TIMEOUT / 2, (
        f"took {overridden:.2f}s, so the call's timeout did not end it"
    )
    # What the generated client's `with_timeout` gets wrong: it rewrites the timeout of the
    # one httpx client every later call shares.
    assert CLIENT_TIMEOUT - 0.05 <= default < CLIENT_TIMEOUT + 1, (
        f"a call with no override gave up after {default:.2f}s"
    )


@pytest.mark.parametrize("call", CLIENT_TIMEOUT_ONLY)
def test_the_clients_timeout_bounds_a_trickling_body_on_a_database_call(
    make_client: ClientFactory, call: str
) -> None:
    bound = LoopBound()
    with SlowBody(trickle=TRICKLE) as server:
        client = make_client(base_url=server.url, timeout=CALL_TIMEOUT, retries=0)
        elapsed = _timed(lambda: CLIENT_TIMEOUT_ONLY[call](client), bound)

    assert elapsed < CLIENT_TIMEOUT / 2, f"took {elapsed:.2f}s"


def test_a_body_that_stalls_after_its_headers_is_bounded(make_client: ClientFactory) -> None:
    bound = LoopBound()
    with SlowBody(trickle=None) as server:
        client = make_client(base_url=server.url, timeout=CLIENT_TIMEOUT, retries=0)
        elapsed = _timed(lambda: client.lookup("9.9.9.9", timeout=CALL_TIMEOUT), bound)

    assert elapsed < CLIENT_TIMEOUT / 2, f"took {elapsed:.2f}s"


def test_the_default_timeout_is_thirty_seconds() -> None:
    for client in (VPNDetection, AsyncVPNDetection):
        assert inspect.signature(client).parameters["timeout"].default == 30


@pytest.mark.parametrize("client", [VPNDetection, AsyncVPNDetection])
@pytest.mark.parametrize("timeout", [0, -1, 0.0, float("nan"), float("inf"), "30", True])
def test_a_timeout_no_attempt_can_meet_is_refused_when_the_client_is_built(
    client: type[VPNDetection | AsyncVPNDetection], timeout: Any
) -> None:
    """Accepted, each of these failed every call instead, after the retries' backoff."""
    with pytest.raises(ValueError, match="timeout"):
        client(timeout=timeout)


@pytest.mark.parametrize("timeout", [None, 0.25, 1, 30])
def test_a_usable_timeout_builds_a_client(timeout: float | None) -> None:
    VPNDetection(timeout=timeout).close()
    asyncio.run(AsyncVPNDetection(timeout=timeout).aclose())


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), "30", True])
@pytest.mark.parametrize("call", PER_CALL_TIMEOUT)
def test_a_per_call_timeout_no_attempt_can_meet_is_refused_before_any_request(
    make_client: ClientFactory, call: str, timeout: Any
) -> None:
    stub = Stub({})
    client = make_client(transport=stub.transport, retries=0)
    clock = FakeClock(LoopBound())
    client.oauth.use_clock(clock)

    with pytest.raises(ValueError, match="timeout"):
        PER_CALL_TIMEOUT[call](client, timeout=timeout)

    assert stub.calls == []
    # The poll waits before its first request, so a check made only there comes too late.
    assert clock.waits == []


@pytest.mark.parametrize("ip", ["10.0.0.1", "1.1.1.1"])
def test_a_per_call_timeout_is_refused_even_when_the_answer_needs_no_request(
    make_client: ClientFactory, ip: str
) -> None:
    """A bogon, and an address already cached."""
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    client = make_client(transport=stub.transport)
    client.lookup("1.1.1.1")

    with pytest.raises(ValueError, match="timeout"):
        client.lookup(ip, timeout=-1)
    with pytest.raises(ValueError, match="timeout"):
        client.lookup_batch([ip], timeout=-1)

    assert len(stub.calls) == 1


def test_the_runtime_vocabularies_are_the_pinned_specs() -> None:
    """`Format` is written by hand, so it is the one that can fall behind a re-pin; the
    generated enums come from the pinned spec, which splits the license type into three
    identical ones, and all three are held to the one list."""
    assert sorted(DATABASE_FORMATS) == sorted(member.value for member in DatabaseFormat)
    assert sorted(STANDINGS) == sorted(member.value for member in Standing)
    for generated in (
        DatabaseLicenseTypeType1,
        DatabaseLicenseTypeType2Type1,
        DatabaseLicenseTypeType3Type1,
    ):
        assert sorted(LICENSE_TYPES) == sorted(member.value for member in generated)


@pytest.mark.parametrize(
    ("wire", "ours"),
    [
        (WireLookupResponse, Result),
        (WireVpnDetail, VpnDetail),
        (WireClassDetail, ClassDetail),
        (WireProxyDetail, ProxyDetail),
        (WireOauthMetadata, OauthMetadata),
        (WireDeviceAuthorization, DeviceAuthorization),
        (WireTokenResponse, TokenResponse),
    ],
)
def test_every_field_the_pinned_spec_serves_is_on_the_model(wire: Any, ours: Any) -> None:
    """The staleness pin on the hand-written models.

    They parse the keys they name and nothing else, so a field a re-pin adds reaches the
    generated code and `raw` while the typed model never hears of it. The generated classes
    come from the same pinned spec, which makes them the list to check against. The
    generator suffixes a name that shadows a builtin with `_`, and spells `mslm:apikey` and
    `mslm:apikey_id` as `mslmapikey` and `mslmapikey_id`, which the model names `apikey` and
    `apikey_id`.
    """
    renamed = {"mslmapikey": "apikey", "mslmapikey_id": "apikey_id"}
    served = {renamed.get(f.name, f.name).rstrip("_") for f in attrs.fields(wire)}
    modeled = {f.name for f in dataclasses.fields(ours)}
    missing = served - {"additional_properties"} - modeled
    assert missing == set(), f"{ours.__name__} lacks what the spec serves: {sorted(missing)}"


@pytest.mark.parametrize("status", [405, 409, 422])
def test_every_4xx_is_the_callers_error_and_never_retried(
    make_client: ClientFactory, status: int
) -> None:
    stub = Stub({"9.9.9.9": {"status": status, "body": {"error": "refused"}}})
    client = make_client(transport=stub.transport, cache=False, retries=2)

    with pytest.raises(VPNDetectionError) as caught:
        client.lookup("9.9.9.9")

    assert caught.value.kind == "bad_request"
    assert caught.value.retryable is False
    assert len(stub.calls) == 1


def test_a_spent_quota_is_never_retried(make_client: ClientFactory) -> None:
    stub = Stub({"9.9.9.9": {"status": 429, "body": {"error": "request allowance exceeded"}}})
    client = make_client(transport=stub.transport, cache=False, retries=3)

    with pytest.raises(VPNDetectionError) as caught:
        client.lookup("9.9.9.9")

    # A 429 with no Retry-After is a spent allowance; knocking again cannot help and
    # would turn a batch into a hammer.
    assert caught.value.kind == "quota_exceeded"
    assert len(stub.calls) == 1


def test_a_rate_limit_is_retried_and_honors_retry_after(make_client: ClientFactory) -> None:
    stub = Stub(
        {
            "9.9.9.9": {
                "status": 429,
                "body": {"error": "rate limit exceeded"},
                "headers": {"Retry-After": "0"},
            }
        }
    )
    client = make_client(transport=stub.transport, cache=False, retries=2)

    with pytest.raises(VPNDetectionError) as caught:
        client.lookup("9.9.9.9")

    assert caught.value.kind == "rate_limited"
    assert len(stub.calls) == 3


def test_a_result_cannot_be_mutated(make_client: ClientFactory) -> None:
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    client = make_client(transport=stub.transport)

    result = client.lookup("1.1.1.1")

    # The cache hands the same object to every later caller of this address.
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.is_vpn = True  # type: ignore[misc]


def test_an_empty_batch_makes_no_request(make_client: ClientFactory) -> None:
    stub = Stub({})
    client = make_client(transport=stub.transport)

    assert client.lookup_batch([]) == {}
    assert stub.calls == []


def test_a_transport_failure_surfaces_as_a_network_error() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with (
        VPNDetection(transport=httpx.MockTransport(refuse), retries=0) as client,
        pytest.raises(VPNDetectionError) as caught,
    ):
        client.lookup("9.9.9.9")

    assert caught.value.kind == "network"
    assert caught.value.retryable is True


def test_a_200_missing_a_required_key_is_a_typed_error_not_a_traceback(
    make_client: ClientFactory,
) -> None:
    """A healthy-looking 200 whose body omits a required property.

    The generated `from_dict` reads required properties by subscript, so this raises
    `KeyError`, not `ValueError`. Catching only the latter let it escape as a bare
    traceback - a caller writing `except VPNDetectionError` saw nothing and crashed.
    """
    stub = Stub({"1.1.1.1": {"status": 200, "body": {"is_vpn": False}}})
    client = make_client(transport=stub.transport, cache=False)

    with pytest.raises(VPNDetectionError) as caught:
        client.lookup("1.1.1.1")

    assert caught.value.kind == "server_error"
    assert "could not read" in str(caught.value)


ENTITLEMENT_BODY = {
    "org_id": "85bb51e4-2eb6-4a31-8e4d-02ba8b98fe61",
    "apikey": {
        "id": "0ab424cc-7619-4dad-b027-afacdc2cedb0",
        "expires": None,
        "allowed_cidrs": [],
    },
    "plan": {"key": "max", "tier": "max"},
    "usage": {
        "requests": 580,
        "quota": 5000000,
        "hard_limit": None,
        "window_start": "2026-09-04T07:00:00Z",
        "window_end": "2026-10-04T07:00:00Z",
    },
}


def test_my_ip_classifies_the_calling_address(make_client: ClientFactory) -> None:
    stub = Stub({"myip": {"body": {"ip": "45.83.91.1", "is_vpn": True}}})
    client = make_client(transport=stub.transport)

    result = client.my_ip()

    assert result.ip == "45.83.91.1"
    assert result.is_vpn is True


def test_my_ip_is_not_cached(make_client: ClientFactory) -> None:
    """The cache is keyed by address, and which address this is IS the question - a
    machine that moves between networks would otherwise be told where it used to be."""
    stub = Stub({"myip": {"body": {"ip": "45.83.91.1", "is_vpn": True}}})
    client = make_client(transport=stub.transport)

    client.my_ip()
    client.my_ip()

    assert len(stub.calls) == 2


def test_my_entitlement_reports_the_plan_and_the_usage(make_client: ClientFactory) -> None:
    stub = Stub({"api/v1/entitlement": {"body": ENTITLEMENT_BODY}})
    client = make_client(transport=stub.transport)

    ent = client.my_entitlement()

    assert ent.plan.key == "max"
    assert ent.plan.tier == "max"
    assert ent.usage.requests == 580
    assert ent.usage.quota == 5000000
    # Null means NEVER stop, which is not the same as a limit of zero.
    assert ent.usage.hard_limit is None
    assert ent.apikey.allowed_cidrs == []


def test_my_entitlement_is_not_cached(make_client: ClientFactory) -> None:
    """The whole point is what has been spent, so a cached answer is a wrong one within
    seconds of the next request."""
    stub = Stub({"api/v1/entitlement": {"body": ENTITLEMENT_BODY}})
    client = make_client(transport=stub.transport)

    client.my_entitlement()
    client.my_entitlement()

    assert len(stub.calls) == 2


def test_my_entitlement_surfaces_an_unauthorized_key(make_client: ClientFactory) -> None:
    """Unlike a lookup there is no useful unauthenticated answer, so this is an error
    rather than a partial result."""
    stub = Stub({"api/v1/entitlement": {"status": 401, "body": {"error": "invalid API key"}}})
    client = make_client(transport=stub.transport, retries=0)

    with pytest.raises(VPNDetectionError):
        client.my_entitlement()


def _timed(call: Callable[[], Any], bound: LoopBound) -> float:
    """How long `call` took to fail, which it must do as a retryable network error."""
    started = time.monotonic()
    outcome = settle(call, bound, within=10.0)
    elapsed = time.monotonic() - started
    assert isinstance(outcome, VPNDetectionError), f"settled with {outcome!r}"
    assert outcome.kind == "network", outcome
    assert outcome.retryable is True
    return elapsed


def _raised(answer: object) -> object:
    """A batch answer, raised when it is an error, so a batch fails the way a lookup does."""
    if isinstance(answer, BaseException):
        raise answer
    return answer

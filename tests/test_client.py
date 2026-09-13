"""The Python-specific API surface, as distinct from the shared conformance corpus."""

from __future__ import annotations

import dataclasses

import httpx
import pytest
from helpers import TESTDATA, ClientFactory, Meter, Stub

from vpndetection import VPNDetection, VPNDetectionError, is_bogon

ADDRESSES = [f"9.9.9.{n}" for n in range(1, 13)]


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

    assert meter.calls == len(ADDRESSES)
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


def test_retries_are_configurable_per_call(make_client: ClientFactory) -> None:
    stub = Stub({"9.9.9.9": {"status": 500, "body": {"error": "lookup failed"}}})
    client = make_client(transport=stub.transport, cache=False, retries=0)

    with pytest.raises(VPNDetectionError):
        client.lookup("9.9.9.9", retries=2)

    # 1 initial attempt plus 2 retries, rather than the instance's 0.
    assert len(stub.calls) == 3


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


ACCOUNT_BODY = {
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


def test_my_account_reports_the_plan_and_the_usage(make_client: ClientFactory) -> None:
    stub = Stub({"api/v1/account/me": {"body": ACCOUNT_BODY}})
    client = make_client(transport=stub.transport)

    account = client.my_account()

    assert account.plan.key == "max"
    assert account.plan.tier == "max"
    assert account.usage.requests == 580
    assert account.usage.quota == 5000000
    # Null means NEVER stop, which is not the same as a limit of zero.
    assert account.usage.hard_limit is None
    assert account.apikey.allowed_cidrs == []


def test_my_account_is_not_cached(make_client: ClientFactory) -> None:
    """The whole point is what has been spent, so a cached answer is a wrong one within
    seconds of the next request."""
    stub = Stub({"api/v1/account/me": {"body": ACCOUNT_BODY}})
    client = make_client(transport=stub.transport)

    client.my_account()
    client.my_account()

    assert len(stub.calls) == 2


def test_my_account_surfaces_an_unauthorized_key(make_client: ClientFactory) -> None:
    """Unlike a lookup there is no useful unauthenticated answer, so this is an error
    rather than a partial result."""
    stub = Stub({"api/v1/account/me": {"status": 401, "body": {"error": "invalid API key"}}})
    client = make_client(transport=stub.transport, retries=0)

    with pytest.raises(VPNDetectionError):
        client.my_account()

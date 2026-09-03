"""Asserts the shared conformance corpus that every VPNDetection SDK asserts.

The corpus is generated into testdata/ and is identical across languages, so a behavior
that drifts here fails here rather than surfacing as two client libraries quietly
disagreeing about the same address.
"""

from __future__ import annotations

from typing import Any

import pytest
from helpers import TESTDATA, ClientFactory, Stub, as_wire

from vpndetection import VPNDetectionError, is_bogon

DETAIL_OBJECTS = ("vpn", "hosting", "dcproxy")


def test_is_bogon_matches_the_canonical_ranges() -> None:
    for case in TESTDATA["isBogon"]:
        assert is_bogon(case["ip"]) is case["expect"], f"{case['ip']} ({case['why']})"


def test_a_bogon_is_answered_locally_in_the_full_max_shape(make_client: ClientFactory) -> None:
    stub = Stub({})
    client = make_client(transport=stub.transport)
    result = client.lookup("10.0.0.1")

    assert result.is_bogon is True
    assert result.ip == "10.0.0.1"
    for flag in TESTDATA["bogonResponse"]["flagsFalse"]:
        assert getattr(result, flag) is False, f"{flag} must be present and false"
    for name in TESTDATA["bogonResponse"]["emptyObjects"]:
        detail = getattr(result, name)
        assert detail is not None and as_wire(detail) == {}, f"{name} must be present and empty"
    assert stub.calls == [], "a bogon must not reach the network"


def test_lookup_preserves_absent_versus_false_across_every_plan_shape(
    make_client: ClientFactory,
) -> None:
    for case in TESTDATA["lookup"]:
        body = case["body"]
        stub = Stub({body["ip"]: {"status": case["status"], "body": body}})
        client = make_client(transport=stub.transport)
        result = client.lookup(body["ip"])
        expect = case["expect"]
        name = case["name"]

        assert result.ip == expect["ip"], name
        assert result.is_bogon is expect["isBogon"], name
        assert result.raw == body, f"{name}: raw must be the wire object"

        for key, value in expect.get("present", {}).items():
            assert getattr(result, key) is value, f"{name}: {key} should be {value}"
        for key in expect.get("absent", []):
            assert getattr(result, key) is None, f"{name}: {key} must be ABSENT, not false"
            if key.startswith("is_"):
                assert result.flagged(key) is False, f"{name}: {key} must coalesce to false"
        for key in expect.get("emptyPresent", []):
            detail = getattr(result, key)
            assert detail is not None and as_wire(detail) == {}, (
                f"{name}: {key} must be present and empty"
            )
        for key in DETAIL_OBJECTS:
            if key in expect:
                assert as_wire(getattr(result, key)) == expect[key], f"{name}: {key}"


def test_a_429_is_classified_by_retry_after_not_by_its_status(make_client: ClientFactory) -> None:
    for case in TESTDATA["errors"]:
        stub = Stub(
            {
                "1.1.1.1": {
                    "status": case["status"],
                    "body": case["body"],
                    "headers": case["headers"],
                }
            }
        )
        # No retries, so a retryable error still surfaces rather than looping.
        client = make_client(transport=stub.transport, retries=0)
        name = case["name"]
        expect = case["expect"]

        with pytest.raises(VPNDetectionError) as caught:
            client.lookup("1.1.1.1")

        err = caught.value
        assert err.kind == expect["kind"], name
        assert err.retryable is expect["retryable"], f"{name}: retryable"
        assert err.status == case["status"], f"{name}: status"
        if "message" in expect:
            assert str(err) == expect["message"], f"{name}: message"
        if "retryAfterSeconds" in expect:
            assert err.retry_after_seconds == expect["retryAfterSeconds"], name


def test_batch_dedupes_short_circuits_bogons_and_keys_by_address(
    make_client: ClientFactory,
) -> None:
    case = _batch("dedup-bogon-and-order-free-keying")
    stub = Stub(
        {
            "1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}},
            "8.8.8.8": {"body": {"ip": "8.8.8.8", "is_vpn": False}},
        }
    )
    client = make_client(transport=stub.transport)
    got = client.lookup_batch(case["input"])

    assert list(got.keys()) == case["expect"]["keys"]
    assert len(stub.calls) == case["expect"]["httpRequests"]
    for key in case["expect"]["bogonKeys"]:
        assert got[key].is_bogon is True, f"{key} should be a local answer"


def test_one_bad_address_does_not_lose_the_rest_of_the_batch(make_client: ClientFactory) -> None:
    case = _batch("partial-failure-does-not-fail-the-batch")
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    client = make_client(transport=stub.transport, retries=0)
    got = client.lookup_batch(case["input"])

    assert list(got.keys()) == case["expect"]["keys"]
    for key in case["expect"]["errorKeys"]:
        assert isinstance(got[key], VPNDetectionError), f"{key} should carry its error"
    assert got["1.1.1.1"].is_vpn is False, "the good address still answered"


def test_a_cache_hit_issues_no_second_request(make_client: ClientFactory) -> None:
    case = _batch("cache-hit-issues-no-second-request")
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    client = make_client(transport=stub.transport)

    for _ in range(case["repeat"]):
        client.lookup_batch(case["input"])
    assert len(stub.calls) == case["expect"]["httpRequests"]


def test_two_clients_never_share_a_cached_answer(make_client: ClientFactory) -> None:
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    a = make_client(transport=stub.transport, api_key="key-a")
    b = make_client(transport=stub.transport, api_key="key-b")

    a.lookup("1.1.1.1")
    b.lookup("1.1.1.1")
    # Two keys can be on different plans and so entitled to different fields; a shared
    # cache would serve one of them the other's shape.
    assert len(stub.calls) == 2


def test_caching_can_be_turned_off(make_client: ClientFactory) -> None:
    stub = Stub({"1.1.1.1": {"body": {"ip": "1.1.1.1", "is_vpn": False}}})
    client = make_client(transport=stub.transport, cache=False)
    client.lookup("1.1.1.1")
    client.lookup("1.1.1.1")
    assert len(stub.calls) == 2


def _batch(name: str) -> dict[str, Any]:
    return next(case for case in TESTDATA["batch"] if case["name"] == name)

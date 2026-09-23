"""The `oauth` accessor against the shared corpus's oauth section, on both clients.

Nothing here reads `oauth.deferred`: those operations are not in this release. Every call
under test runs through `settle`, so a loop that never ends fails its test instead of
hanging the suite.
"""

from __future__ import annotations

import asyncio
import time
import urllib.parse
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
from helpers import (
    TESTDATA,
    ClientFactory,
    FakeClock,
    LoopBound,
    OauthAdapter,
    OauthStub,
    settle,
)

from vpndetection import (
    AsyncVPNDetection,
    DeviceAuthorization,
    OauthAccessDeniedError,
    OauthError,
    OauthExpiredTokenError,
    TokenResponse,
    VPNDetectionError,
    _core,
)

CORPUS: dict[str, Any] = TESTDATA["oauth"]

BASE_URL = "https://api.example.test"
DEVICE_CODE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"

# Satisfies every operation's required members at once.
EVERY_REQUIRED_MEMBER = {
    "issuer": BASE_URL,
    "authorization_endpoint": f"{BASE_URL}/oauth/authorize",
    "token_endpoint": f"{BASE_URL}/oauth/token",
    "device_code": "mo_dc_x",
    "user_code": "BCDF-GHJK",
    "verification_uri": "https://app.example.test/device",
    "expires_in": 900,
    "interval": 5,
    "access_token": "mo_at_x",
    "token_type": "Bearer",
}

DEVICE = DeviceAuthorization(
    device_code="mo_dc_x",
    user_code="BCDF-GHJK",
    verification_uri="https://app.example.test/device",
    expires_in=900,
    interval=5,
)

# In the corpus's production document, but no longer advertised or in the pinned spec, so it
# is not a member of OauthMetadata.
NOT_A_MEMBER = {"client_id_metadata_document_supported"}


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Retried answers without the real backoff's seconds of waiting."""
    monkeypatch.setattr(_core, "_BACKOFF_BASE", 0.0)
    yield


def test_no_oauth_request_carries_the_api_key(make_client: ClientFactory) -> None:
    case = CORPUS["noCredential"]
    key = case["apiKey"]
    bound = LoopBound()
    stub = OauthStub([{"status": 200, "body": EVERY_REQUIRED_MEMBER}], bound)
    client = make_client(api_key=key, base_url=BASE_URL, transport=stub.transport, retries=0)
    client.oauth.use_clock(FakeClock(bound))

    outcome = settle(lambda: _every_operation(client.oauth), bound)

    assert outcome is None, f"settled with {outcome!r}"
    assert len(stub.requests) == 6
    for req in stub.requests:
        label = f"{req.method} {req.url.path}"
        for name in case["forbiddenHeaders"]:
            assert name not in req.headers, f"{label} carried {name}"
        for name in case["forbiddenQuery"]:
            assert name not in req.url.params, f"{label} carried ?{name}"
        assert key not in str(req.url), label
        assert all(key not in value for value in req.headers.values()), label
        assert key.encode() not in req.content, label

    # The same client does send the key where it belongs, so the checks above are not vacuous.
    settle(lambda: client.my_ip(), bound)
    assert stub.requests[-1].headers["authorization"] == f"Bearer {key}"


@pytest.mark.parametrize("case", CORPUS["forms"]["cases"], ids=lambda case: case["name"])
def test_each_operation_requests_its_endpoint_with_exactly_its_form_fields(
    make_client: ClientFactory, case: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub([{"status": 200, "body": EVERY_REQUIRED_MEMBER}], bound)
    # No key at all: none is needed to sign in.
    client = make_client(base_url=BASE_URL, transport=stub.transport)

    outcome = settle(lambda: _call(client.oauth, case["operation"], case["args"]), bound)

    assert not isinstance(outcome, BaseException), f"settled with {outcome!r}"
    [req] = stub.requests
    _assert_endpoint(req, CORPUS["endpoints"][case["endpoint"]])
    assert req.headers["content-type"].startswith(CORPUS["forms"]["contentType"])
    assert _form_fields(req.content) == case["fields"]


def test_metadata_is_a_get_of_the_discovery_document_under_the_base_url(
    make_client: ClientFactory,
) -> None:
    bound = LoopBound()
    stub = OauthStub([{"status": 200, "body": EVERY_REQUIRED_MEMBER}], bound)
    client = make_client(base_url=f"{BASE_URL}/", transport=stub.transport)

    settle(lambda: client.oauth.metadata(), bound)

    [req] = stub.requests
    _assert_endpoint(req, CORPUS["endpoints"]["metadata"])
    assert str(req.url) == f"{BASE_URL}{CORPUS['endpoints']['metadata']['path']}"
    assert req.content == b""


@pytest.mark.parametrize(
    ("operation", "case"),
    [
        (operation, case)
        for section, operations in (
            ("metadata", ["metadata"]),
            ("deviceAuthorization", ["deviceAuthorization"]),
            ("token", ["exchangeDeviceCode", "exchangeRefreshToken"]),
        )
        for case in CORPUS["responses"][section]
        for operation in operations
    ],
    ids=lambda value: value if isinstance(value, str) else value["name"],
)
def test_a_2xx_decodes_on_presence(
    make_client: ClientFactory, operation: str, case: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub([case], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport)

    got = settle(lambda: _call(client.oauth, operation, _ARGS[operation]), bound)

    assert not isinstance(got, BaseException), f"settled with {got!r}"
    for name, value in case["expect"]["present"].items():
        if name in NOT_A_MEMBER:
            continue
        member = getattr(got, name)
        assert (list(member) if isinstance(member, tuple) else member) == value, name
    for name in case["expect"]["absent"]:
        assert getattr(got, name) is None, f"{name} should be absent"


@pytest.mark.parametrize("case", CORPUS["responses"]["revoke"], ids=lambda case: case["name"])
def test_revoke_reads_no_body(make_client: ClientFactory, case: dict[str, Any]) -> None:
    bound = LoopBound()
    stub = OauthStub([case], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport)

    outcome = settle(lambda: client.oauth.revoke("vpndetection-cli", "mo_rt_x"), bound)

    assert outcome is None, f"settled with {outcome!r}"


@pytest.mark.parametrize("operation", ["metadata", "deviceAuthorization", "exchangeDeviceCode"])
@pytest.mark.parametrize(
    "reply",
    [
        {"status": 200, "body": {}},
        {"status": 200, "rawBody": "<html>not json</html>"},
        {
            "status": 200,
            "body": {**EVERY_REQUIRED_MEMBER, "issuer": 7, "user_code": 7, "access_token": 7},
        },
        {"status": 200, "body": ["not", "an", "object"]},
    ],
    ids=["missing-members", "not-json", "wrong-type", "not-an-object"],
)
def test_a_2xx_that_lacks_a_member_or_does_not_parse_is_the_ordinary_error(
    make_client: ClientFactory, operation: str, reply: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub([reply], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport, retries=0)

    outcome = settle(lambda: _call(client.oauth, operation, _ARGS[operation]), bound)

    _assert_outcome(outcome, {"type": "client", "kind": "server_error", "status": 200}, operation)


# No corpus case: every response there decodes. One member left out per case, since a body
# missing all of them at once passes against a decoder that defaults any single one.
@pytest.mark.parametrize(
    ("operation", "member"),
    [
        (operation, member)
        for operation, members in (
            ("metadata", ["issuer", "authorization_endpoint", "token_endpoint"]),
            (
                "deviceAuthorization",
                ["device_code", "user_code", "verification_uri", "expires_in", "interval"],
            ),
            ("exchangeDeviceCode", ["access_token", "token_type", "expires_in"]),
        )
        for member in members
    ],
)
def test_an_answer_missing_any_one_required_member_is_the_ordinary_error(
    make_client: ClientFactory, operation: str, member: str
) -> None:
    body = {name: value for name, value in EVERY_REQUIRED_MEMBER.items() if name != member}
    bound = LoopBound()
    stub = OauthStub([{"status": 200, "body": body}], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport, retries=0)

    outcome = settle(lambda: _call(client.oauth, operation, _ARGS[operation]), bound)

    _assert_outcome(outcome, {"type": "client", "kind": "server_error", "status": 200}, member)


@pytest.mark.parametrize("case", CORPUS["errors"]["cases"], ids=lambda case: case["name"])
def test_a_failed_answer_is_an_oauth_refusal_only_when_it_is_one(
    make_client: ClientFactory, case: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub([case], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport)

    outcome = settle(
        lambda: client.oauth.exchange_device_code("vpndetection-cli", "mo_dc_x"), bound
    )

    _assert_outcome(outcome, case["expect"], case["name"])


@pytest.mark.parametrize("case", CORPUS["retries"]["cases"], ids=lambda case: case["name"])
def test_only_what_consumes_nothing_is_retried(
    make_client: ClientFactory, case: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub(case["responses"], bound)
    # The client's default retries, which is what the corpus counts against.
    client = make_client(base_url=BASE_URL, transport=stub.transport)

    outcome = settle(lambda: _call(client.oauth, case["operation"], case["args"]), bound)

    expect = case["expect"]
    assert len(stub.requests) == expect["requests"], "requests sent"
    if expect["outcome"] == "ok":
        assert not isinstance(outcome, BaseException), f"settled with {outcome!r}"
    else:
        _assert_outcome(outcome, {**expect, "type": expect["outcome"]}, case["name"])


@pytest.mark.parametrize("case", CORPUS["poll"]["cases"], ids=lambda case: case["name"])
def test_poll_device_token_waits_widens_and_ends_as_the_corpus_says(
    make_client: ClientFactory, case: dict[str, Any]
) -> None:
    bound = LoopBound()
    stub = OauthStub(case["responses"], bound)
    client = make_client(base_url=BASE_URL, transport=stub.transport)
    clock = FakeClock(bound)
    client.oauth.use_clock(clock)
    device = DeviceAuthorization(**case["device"])

    outcome = settle(lambda: client.oauth.poll_device_token(case["clientId"], device), bound)

    expect = case["expect"]
    assert clock.waits == expect["waits"], "waits, in seconds"
    assert len(stub.requests) == expect["requests"], "requests sent"
    form = {
        "grant_type": DEVICE_CODE_GRANT,
        "device_code": device.device_code,
        "client_id": case["clientId"],
    }
    for req in stub.requests:
        _assert_endpoint(req, CORPUS["endpoints"]["token"])
        assert _form_fields(req.content) == form
    if expect["outcome"] == "token":
        assert isinstance(outcome, TokenResponse), f"settled with {outcome!r}"
        assert outcome.access_token == expect.get("token", {}).get(
            "access_token", outcome.access_token
        )
        return
    _assert_outcome(outcome, {**expect, "type": expect["outcome"]}, case["name"])


def test_cancelling_a_poll_during_its_first_wait_ends_it_at_once() -> None:
    bound = LoopBound()
    stub = OauthStub([{"status": 400, "body": {"error": "authorization_pending"}}], bound, limit=1)

    async def cancelled_after() -> float | None:
        async with AsyncVPNDetection(base_url=BASE_URL, transport=stub.transport) as client:
            poll = asyncio.create_task(client.oauth.poll_device_token("vpndetection-cli", DEVICE))
            await asyncio.sleep(0.1)
            started = time.monotonic()
            poll.cancel()
            try:
                await poll
            except asyncio.CancelledError:
                return time.monotonic() - started
            return None

    elapsed = settle(lambda: asyncio.run(cancelled_after()), bound, within=3.0)

    assert isinstance(elapsed, float), f"the poll settled with {elapsed!r} rather than cancelling"
    assert elapsed < 1.0, f"settled {elapsed:.2f}s after the cancel"
    assert stub.requests == [], "no request after the cancel"


def _every_operation(oauth: OauthAdapter) -> None:
    oauth.metadata()
    oauth.device_authorization("vpndetection-cli", scope="account.read")
    oauth.exchange_device_code("vpndetection-cli", "mo_dc_x")
    oauth.exchange_refresh_token("vpndetection-cli", "mo_rt_x")
    oauth.revoke("vpndetection-cli", "mo_rt_x")
    oauth.poll_device_token("vpndetection-cli", DEVICE)


# Arguments that satisfy each operation, for the cases that are about the answer.
_ARGS: dict[str, dict[str, str]] = {
    "metadata": {},
    "deviceAuthorization": {"clientId": "vpndetection-cli"},
    "exchangeDeviceCode": {"clientId": "vpndetection-cli", "deviceCode": "mo_dc_x"},
    "exchangeRefreshToken": {"clientId": "vpndetection-cli", "refreshToken": "mo_rt_x"},
}


def _call(oauth: OauthAdapter, operation: str, args: dict[str, str]) -> Any:
    if operation == "metadata":
        return oauth.metadata()
    if operation == "deviceAuthorization":
        return oauth.device_authorization(
            args["clientId"], scope=args.get("scope"), resource=args.get("resource")
        )
    if operation == "exchangeDeviceCode":
        return oauth.exchange_device_code(args["clientId"], args["deviceCode"])
    if operation == "exchangeRefreshToken":
        return oauth.exchange_refresh_token(args["clientId"], args["refreshToken"])
    if operation == "revoke":
        return oauth.revoke(args["clientId"], args["token"])
    raise AssertionError(f"the corpus names an operation this suite does not know: {operation}")


def _assert_endpoint(req: httpx.Request, want: dict[str, str]) -> None:
    assert f"{req.method} {req.url.path}" == f"{want['method']} {want['path']}"


# A form body as a field map, decoded the way a server decodes it (+ is a space).
def _form_fields(body: bytes) -> dict[str, str]:
    fields: dict[str, str] = {}
    for name, value in urllib.parse.parse_qsl(body.decode(), keep_blank_values=True):
        assert name not in fields, f"{name} sent twice"
        fields[name] = value
    return fields


# `type` is oauth (the base class exactly), accessDenied, expiredToken, or client: the
# ordinary error, which is never an OauthError. A null in the corpus is Python's None.
def _assert_outcome(err: Any, want: dict[str, Any], label: str) -> None:
    assert isinstance(err, VPNDetectionError), f"{label}: settled with {err!r}"
    got = f"{label}: settled with {err!r}"
    subtype = isinstance(err, (OauthAccessDeniedError, OauthExpiredTokenError))
    if want["type"] == "oauth":
        assert isinstance(err, OauthError) and not subtype, f"{got}, want the base OauthError"
    elif want["type"] == "accessDenied":
        assert isinstance(err, OauthAccessDeniedError), f"{got}, want OauthAccessDeniedError"
    elif want["type"] == "expiredToken":
        assert isinstance(err, OauthExpiredTokenError), f"{got}, want OauthExpiredTokenError"
    else:
        assert want["type"] == "client", f"{label}: unknown outcome {want['type']}"
        assert not isinstance(err, OauthError), f"{got}, want the ordinary error"
    fields = {
        "errorCode": "error_code",
        "errorDescription": "error_description",
        "status": "status",
        "kind": "kind",
        "retryable": "retryable",
    }
    for wire, name in fields.items():
        if wire in want:
            assert getattr(err, name) == want[wire], f"{label}: {name}"
    if "message" in want:
        assert str(err) == want["message"], f"{label}: message"

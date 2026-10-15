"""What each call makes of an answer it cannot read, and of a 4xx whose body is not the API's.

A 2xx no call can read is the server's failure: a retried `server_error` carrying the status,
never a raw error and never a hole handed back as the answer. A 4xx is classified by its
status alone, whatever its body, and sent once. 5.7.1 sent a `null` 200 once and raised a raw
`TypeError`, carried no status on the rest, and decoded a proxy's HTML 401, an empty 403 or
an HTML 429 into a retried `server_error`, sent three times (measured 2026-10-15).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from helpers import ClientFactory

from vpndetection import Result, VPNDetectionError, _core

LOOKUP = {"ip": "8.8.8.8", "is_vpn": False}

DATABASE: dict[str, Any] = {
    "base": "vpn_ip",
    "name": "VPN IP",
    "summary": "Addresses VPN providers exit from.",
    "license_type": None,
    "starts": None,
    "expires": None,
    "renews_at": None,
    "notice_due_at": None,
    "in_term": False,
    "standing": "unlicensed",
    "versions": [],
}

DOWNLOAD: dict[str, Any] = {
    "dataset_id": "vpn_ip_v1",
    "format": "mmdb",
    "outcome": "ok",
    "sample": False,
    "bytes": None,
    "http_status": None,
    "apikey_id": None,
    "client_ip": None,
    "user_agent": None,
    "created": "2026-10-15T06:00:00Z",
}

CALLS: dict[str, tuple[str, Callable[[Any], Any]]] = {
    "lookup": ("/8.8.8.8", lambda c: c.lookup("8.8.8.8")),
    "my_ip": ("/myip", lambda c: c.my_ip()),
    "my_entitlement": ("/api/v1/entitlement", lambda c: c.my_entitlement()),
    "list": ("/api/v1/database/list", lambda c: c.database.list()),
    "metadata": ("/api/v1/database/metadata", lambda c: c.database.metadata("vpn_ip_v1")),
    "checksums": (
        "/api/v1/database/checksum",
        lambda c: c.database.checksums("vpn_ip_v1", "mmdb"),
    ),
    "downloads": ("/api/v1/database/downloads", lambda c: c.database.downloads()),
    "download_url": (
        "/api/v1/database/download",
        lambda c: c.database.download_url("vpn_ip_v1", "mmdb"),
    ),
}

UNREADABLE = {
    "HTML": "<html><body>502 Bad Gateway</body></html>",
    "empty": "",
    "null": "null",
    "a list": "[]",
    "an empty object": "{}",
    "cut off": '{"ip": "8.8.8.8", "is_',
}

NOT_THE_APIS = {
    "HTML 400": (400, "<html>400</html>", "bad_request"),
    "HTML 401": (401, "<html>401</html>", "unauthorized"),
    "empty 403": (403, "", "forbidden"),
    "HTML 404": (404, "<html>404</html>", "bad_request"),
    "HTML 429": (429, "<html>429</html>", "quota_exceeded"),
}


class Raw:
    """Answers every request with one status and body, and counts what reached it."""

    def __init__(self, status: int, body: str) -> None:
        self.paths: list[str] = []
        self.transport = httpx.MockTransport(self._handle)
        self._status = status
        self._body = body

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.paths.append(request.url.path)
        return httpx.Response(
            self._status, content=self._body.encode(), headers={"content-type": "text/html"}
        )


def outcome_of(call: Callable[[], Any]) -> Any:
    try:
        return call()
    except VPNDetectionError as err:
        return err


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_core, "_BACKOFF_BASE", 0.0)


@pytest.mark.parametrize("body", list(UNREADABLE.values()), ids=list(UNREADABLE))
@pytest.mark.parametrize("name", list(CALLS))
def test_an_unreadable_2xx_is_a_retried_server_error_carrying_its_status(
    make_client: ClientFactory, name: str, body: str
) -> None:
    path, call = CALLS[name]
    origin = Raw(200, body)
    client = make_client(transport=origin.transport, cache=False, retries=2)

    outcome = outcome_of(lambda: call(client))

    assert isinstance(outcome, VPNDetectionError), f"{name} answered {outcome!r}"
    assert (outcome.kind, outcome.status) == ("server_error", 200), repr(outcome)
    assert origin.paths == [path] * 3


@pytest.mark.parametrize("reply", list(NOT_THE_APIS.values()), ids=list(NOT_THE_APIS))
@pytest.mark.parametrize("name", list(CALLS))
def test_a_4xx_whose_body_is_not_the_apis_is_classified_by_its_status_and_sent_once(
    make_client: ClientFactory, name: str, reply: tuple[int, str, str]
) -> None:
    status, body, kind = reply
    path, call = CALLS[name]
    origin = Raw(status, body)
    client = make_client(transport=origin.transport, cache=False, retries=2)

    outcome = outcome_of(lambda: call(client))

    assert isinstance(outcome, VPNDetectionError), f"{name} answered {outcome!r}"
    assert (outcome.kind, outcome.status) == (kind, status), repr(outcome)
    assert origin.paths == [path]


MALFORMED = {
    "a lookup's ip null": ("lookup", {**LOOKUP, "ip": None}),
    "a lookup's is_vpn a string": ("lookup", {**LOOKUP, "is_vpn": "yes"}),
    "a lookup's is_hosting a number": ("lookup", {**LOOKUP, "is_hosting": 1}),
    "my_ip's ip null": ("my_ip", {**LOOKUP, "ip": None}),
    "databases null": ("list", {"databases": None}),
    "a database null": ("list", {"databases": [None]}),
    "a database's base null": ("list", {"databases": [{**DATABASE, "base": None}]}),
    "a database's versions null": ("list", {"databases": [{**DATABASE, "versions": None}]}),
    "downloads null": ("downloads", {"downloads": None}),
    "a download's dataset_id null": (
        "downloads",
        {"downloads": [{**DOWNLOAD, "dataset_id": None}]},
    ),
    "checksums null": ("checksums", {"id": "vpn_ip_v1", "format": "mmdb", "checksums": None}),
}


@pytest.mark.parametrize("case", list(MALFORMED.values()), ids=list(MALFORMED))
def test_a_member_the_api_always_sends_sent_as_null_or_the_wrong_type_is_its_failure(
    make_client: ClientFactory, case: tuple[str, dict[str, Any]]
) -> None:
    name, body = case
    path, call = CALLS[name]
    origin = Raw(200, json.dumps(body))
    client = make_client(transport=origin.transport, cache=False, retries=2)

    outcome = outcome_of(lambda: call(client))

    assert isinstance(outcome, VPNDetectionError), f"{name} answered {outcome!r}"
    assert (outcome.kind, outcome.status) == ("server_error", 200), repr(outcome)
    assert origin.paths == [path] * 3


def test_the_fixtures_above_read_as_answers(make_client: ClientFactory) -> None:
    # Each malformed case is one member away from these, so they must read as they are.
    for name, body in [
        ("list", {"databases": [DATABASE]}),
        ("downloads", {"downloads": [DOWNLOAD]}),
    ]:
        path, call = CALLS[name]
        origin = Raw(200, json.dumps(body))
        client = make_client(transport=origin.transport, cache=False, retries=2)

        assert len(call(client)) == 1
        assert origin.paths == [path]


ENTRIES: dict[str, Any] = {
    "null": None,
    "a list": [],
    "an empty object": {},
    "ip null": {**LOOKUP, "ip": None},
    "is_vpn a string": {**LOOKUP, "is_vpn": "yes"},
}


@pytest.mark.parametrize("entry", list(ENTRIES.values()), ids=list(ENTRIES))
def test_a_batch_entry_it_cannot_read_is_that_addresss_error_alone(
    make_client: ClientFactory, entry: Any
) -> None:
    body = {"results": {"8.8.8.8": entry, "1.1.1.1": {**LOOKUP, "ip": "1.1.1.1"}}}
    origin = Raw(200, json.dumps(body))
    client = make_client(transport=origin.transport, cache=False, retries=2)

    answers = client.lookup_batch(["8.8.8.8", "1.1.1.1"])

    failed = answers["8.8.8.8"]
    assert isinstance(failed, VPNDetectionError), repr(failed)
    assert (failed.kind, failed.status) == ("server_error", 200)
    assert isinstance(answers["1.1.1.1"], Result)
    assert origin.paths == ["/batch"]


@pytest.mark.parametrize(
    "body",
    ["<html>502</html>", "", "null", "[]", "{}", '{"results": null}', '{"results": []}'],
    ids=["HTML", "empty", "null", "a list", "neither map", "results null", "results a list"],
)
def test_a_batch_answer_holding_neither_map_fails_its_chunk_retried(
    make_client: ClientFactory, body: str
) -> None:
    origin = Raw(200, body)
    client = make_client(transport=origin.transport, cache=False, retries=2)

    answers = client.lookup_batch(["8.8.8.8", "1.1.1.1"])

    for ip in ("8.8.8.8", "1.1.1.1"):
        failed = answers[ip]
        assert isinstance(failed, VPNDetectionError), f"{ip}: {failed!r}"
        assert (failed.kind, failed.status) == ("server_error", 200), repr(failed)
    assert origin.paths == ["/batch"] * 3


class Keys:
    """Answers a lookup, and keeps the Authorization header of each request."""

    def __init__(self) -> None:
        self.authorization: list[str | None] = []
        self.transport = httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.authorization.append(request.headers.get("authorization"))
        return httpx.Response(200, json=LOOKUP)


@pytest.mark.parametrize("api_key", [None, "", "   ", "\t", "\r\n"])
def test_a_key_of_blanks_alone_is_no_key(make_client: ClientFactory, api_key: str | None) -> None:
    """5.7.1 sent a key of blanks as one, which httpx refuses, so every call failed as a
    retried network error with nothing sent."""
    origin = Keys()
    client = make_client(transport=origin.transport, cache=False, api_key=api_key)

    client.lookup("8.8.8.8")

    assert origin.authorization == [None]


def test_the_api_key_is_trimmed(make_client: ClientFactory) -> None:
    """A key pasted with a line ending around it went out padded, which httpx refuses, so
    every call failed as a retried network error with nothing sent (5.7.1)."""
    origin = Keys()
    client = make_client(transport=origin.transport, cache=False, api_key=" key\r\n")

    client.lookup("8.8.8.8")

    assert origin.authorization == ["Bearer key"]


@pytest.mark.parametrize(
    "api_key", ["key\r\nX-Injected: 1", "ke\ty", "key\x00", "key\x7f", "k\ney", "k\x85ey", "kéy"]
)
def test_a_control_character_or_one_outside_ascii_is_refused_where_the_key_is_set(
    make_client: ClientFactory, api_key: str
) -> None:
    """Accepted, a CR, LF or NUL failed every call as a retried network error with nothing
    sent, a character outside ASCII as a server_error, and a tab or DEL went out on the wire
    inside the header (5.7.1)."""
    with pytest.raises(ValueError, match="control character"):
        make_client(api_key=api_key)


class Paths:
    """Answers each call with what it needs, and keeps every path that reached it."""

    def __init__(self) -> None:
        self.paths: list[str] = []
        self.transport = httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.paths.append(request.url.path)
        if request.url.path.endswith("/batch"):
            return httpx.Response(200, json={"results": {"8.8.8.8": LOOKUP}, "errors": {}})
        if request.url.path.endswith("/list"):
            return httpx.Response(200, json={"databases": []})
        if request.url.path.endswith("oauth-authorization-server"):
            return httpx.Response(
                200,
                json={
                    "issuer": "https://api.example.test",
                    "authorization_endpoint": "https://api.example.test/oauth/authorize",
                    "token_endpoint": "https://api.example.test/oauth/token",
                },
            )
        return httpx.Response(200, json=LOOKUP)


@pytest.mark.parametrize("slashes", [1, 2, 3])
def test_every_trailing_slash_on_the_base_url_is_dropped(
    make_client: ClientFactory, slashes: int
) -> None:
    """httpx dropped one when it joined a path on, and a second reached the API as
    `//8.8.8.8` (5.7.1)."""
    origin = Paths()
    client = make_client(
        transport=origin.transport, cache=False, base_url="https://api.example.test" + "/" * slashes
    )

    client.lookup("8.8.8.8")
    client.my_ip()
    client.lookup_batch(["8.8.8.8"])
    client.database.list()
    client.oauth.metadata()

    assert origin.paths == [
        "/8.8.8.8",
        "/myip",
        "/batch",
        "/api/v1/database/list",
        "/.well-known/oauth-authorization-server",
    ]

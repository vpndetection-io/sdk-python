"""What a client makes of the key and the base URL it is given: the key trimmed, refused
where it is set when no header can carry it, and every trailing slash dropped from the URL.
"""

from __future__ import annotations

import httpx
import pytest
from helpers import ClientFactory

LOOKUP = {"ip": "8.8.8.8", "is_vpn": False}


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

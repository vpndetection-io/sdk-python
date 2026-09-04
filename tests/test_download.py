"""The dataset download path.

What these methods do with a `302` and with a body too large to hold is the whole point
of them, so the double here serves both legs: the API's redirect on one host and the
object storage it points at on another. That is what lets a test assert where the API
key went, and where it did not.
"""

from __future__ import annotations

import gzip
import tracemalloc
from collections.abc import AsyncIterator, Iterator
from dataclasses import dataclass
from pathlib import Path

import httpx
import pytest
from helpers import ClientAdapter, ClientFactory

from vpndetection import VPNDetectionError

API = "https://api.example"
STORAGE = "https://storage.example"
BLOB = f"{STORAGE}/blob"
API_KEY = "secret-key"

SMALL = b"id,provider\n45.83.91.1,mullvad\n"
# One chunk, reused, so a test can serve gigabytes without allocating them.
FILLER = bytes(1 << 20)


@dataclass(frozen=True)
class Blob:
    """What object storage serves.

    A `size` of zero is the small CSV nearly every test wants. Above that the body is
    synthetic, and `delivered` under `size` promises a whole dataset and cuts it short,
    which is the silent truncation a client has to catch. `dies` makes that shortfall
    arrive as a dropped connection instead of a clean end of body.
    """

    size: int = 0
    delivered: int | None = None
    dies: bool = False
    status: int = 200
    encoding: str | None = None


class Origin:
    """The API and the object storage it redirects to, on one transport.

    Both legs go through the same transport, so one record holds the request that
    carries the key and the one that must not.
    """

    def __init__(self, blob: Blob) -> None:
        self.blob = blob
        self.requests: list[httpx.Request] = []
        self.transport = httpx.MockTransport(self._handle)
        self.client: ClientAdapter

    def paths(self) -> list[str]:
        return [request.url.path for request in self.requests]

    def request(self, path: str) -> httpx.Request:
        for request in self.requests:
            if request.url.path == path:
                return request
        pytest.fail(f"the origin was never asked for {path}, it saw {self.paths()}")

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path == "/api/v1/database/download":
            # Absolute, as the real 302 is: a presigned URL is on another host entirely,
            # so nothing here may lean on a relative one.
            return httpx.Response(302, headers={"Location": BLOB})
        if str(request.url) != BLOB:
            return httpx.Response(404, json={"rc": "NO_SUCH_PATH"})
        if self.blob.status != 200:
            return httpx.Response(self.blob.status, content=b"<Error><Code>AccessDenied</Code>")

        headers = {"Content-Length": str(self._promised())}
        if self.blob.encoding is not None:
            headers["Content-Encoding"] = self.blob.encoding
        return httpx.Response(200, headers=headers, stream=BlobStream(self.blob))

    def _promised(self) -> int:
        if self.blob.encoding is not None:
            return len(gzip.compress(SMALL))
        return self.blob.size or len(SMALL)


class BlobStream(httpx.SyncByteStream, httpx.AsyncByteStream):
    """The blob's bytes, in chunks, so the client is measured rather than the fixture."""

    def __init__(self, blob: Blob) -> None:
        self._blob = blob

    def __iter__(self) -> Iterator[bytes]:
        yield from self._chunks()

    async def __aiter__(self) -> AsyncIterator[bytes]:
        for chunk in self._chunks():
            yield chunk

    def _chunks(self) -> Iterator[bytes]:
        if self._blob.encoding is not None:
            yield gzip.compress(SMALL)
            return
        if self._blob.size == 0:
            yield SMALL
            return
        remaining = self._blob.size if self._blob.delivered is None else self._blob.delivered
        while remaining > 0:
            step = min(remaining, len(FILLER))
            yield FILLER[:step]
            remaining -= step
        if self._blob.dies:
            raise httpx.ReadError("the connection dropped mid-transfer")


def origin(make_client: ClientFactory, blob: Blob | None = None) -> Origin:
    served = Origin(blob or Blob())
    served.client = make_client(
        api_key=API_KEY, base_url=API, transport=served.transport, cache=False
    )
    return served


def part_of(path: Path) -> Path:
    return Path(f"{path}.part")


def test_download_follows_the_redirect_and_writes_the_file(
    make_client: ClientFactory, tmp_path: Path
) -> None:
    served = origin(make_client)
    path = tmp_path / "cdn_ip_v1.csv.gz"

    written = served.client.database.download("cdn_ip_v1", "csvgz", path)

    assert written == len(SMALL)
    assert path.read_bytes() == SMALL
    assert not part_of(path).exists(), "the .part file outlived a successful transfer"
    assert served.paths() == ["/api/v1/database/download", "/blob"]


def test_download_bytes_hands_back_the_same_bytes(make_client: ClientFactory) -> None:
    served = origin(make_client)

    assert served.client.database.download_bytes("cdn_ip_v1", "csvgz") == SMALL


def test_download_url_hands_back_the_link_without_fetching_it(
    make_client: ClientFactory,
) -> None:
    served = origin(make_client)

    assert served.client.database.download_url("cdn_ip_v1", "csvgz") == BLOB
    assert served.paths() == ["/api/v1/database/download"]


# The key authorizes the API call that mints the link. The link is presigned and
# authorizes itself, so forwarding the key on would hand a credential to a host that has
# no business seeing it.
def test_the_api_key_reaches_the_api_and_never_object_storage(
    make_client: ClientFactory, tmp_path: Path
) -> None:
    served = origin(make_client)

    served.client.database.download("cdn_ip_v1", "csvgz", tmp_path / "keys.csv.gz")

    api = served.request("/api/v1/database/download")
    assert API_KEY in api.headers.get("authorization", ""), (
        "the API request carried no key, so this proves nothing about the second one"
    )
    storage = served.request("/blob")
    for name, value in storage.headers.items():
        assert API_KEY not in value, f"the key leaked to object storage in {name}: {value}"
    assert storage.url.query == b"", "the storage request carried a query string"


def test_object_storage_refusing_the_link_is_not_reported_as_a_lookup_failure(
    make_client: ClientFactory,
) -> None:
    served = origin(make_client, Blob(status=403))

    with pytest.raises(VPNDetectionError) as caught:
        served.client.database.download_bytes("cdn_ip_v1", "csvgz")

    assert caught.value.kind == "forbidden"
    assert caught.value.retryable is False
    assert "object storage" in caught.value.message, "the message does not say which host refused"
    assert len(served.requests) == 2, "a refused link is not worth retrying"


# A truncated file that looks complete is worse than no file: the next run reads it as a
# whole dataset. A transfer can end short without any error reaching the client, so what
# arrived has to be checked against what was promised.
def test_a_short_transfer_fails_loudly_and_leaves_nothing_behind(
    make_client: ClientFactory, tmp_path: Path
) -> None:
    served = origin(make_client, Blob(size=4 << 20, delivered=1 << 20))
    path = tmp_path / "half-a-dataset.csv.gz"

    with pytest.raises(VPNDetectionError) as caught:
        served.client.database.download("cdn_ip_v1", "csvgz", path)

    assert caught.value.kind == "network"
    assert "of 4194304 bytes" in caught.value.message
    assert not path.exists(), "a truncated file is sitting at the destination"
    assert not part_of(path).exists(), "the .part file was left behind"


def test_download_bytes_refuses_a_short_body_rather_than_returning_it(
    make_client: ClientFactory,
) -> None:
    served = origin(make_client, Blob(size=4 << 20, delivered=1 << 20))

    with pytest.raises(VPNDetectionError) as caught:
        served.client.database.download_bytes("cdn_ip_v1", "csvgz")

    assert caught.value.kind == "network"


# The half of the .part guard a cleanup step cannot fake: a destination opened directly
# is truncated before the first byte arrives, so yesterday's good copy is gone whether or
# not the refresh then succeeds.
def test_a_failed_refresh_leaves_the_previous_copy_intact(
    make_client: ClientFactory, tmp_path: Path
) -> None:
    served = origin(make_client, Blob(size=4 << 20, delivered=1 << 20, dies=True))
    path = tmp_path / "cdn_ip_v1.csv.gz"
    path.write_bytes(SMALL)

    # A failure DURING the transfer surfaces as it happened rather than as the library's
    # error type: a reset socket and a full disk are different problems, and only one of
    # them is ours.
    with pytest.raises(httpx.ReadError):
        served.client.database.download("cdn_ip_v1", "csvgz", path)

    assert path.read_bytes() == SMALL, "the previous copy did not survive"
    assert not part_of(path).exists(), "the .part file was left behind"


# The assertion that matters most: a body far larger than any sane buffer has to move
# through the process without ever being resident. The threshold is an eighth of the
# payload, so a buffering implementation cannot slip under it.
def test_a_large_body_is_streamed_rather_than_held(
    make_client: ClientFactory, tmp_path: Path
) -> None:
    size = 64 << 20
    served = origin(make_client, Blob(size=size))
    path = tmp_path / "vpn_ip_extended_v1.mmdb"

    tracemalloc.start()
    try:
        written = served.client.database.download("vpn_ip_extended_v1", "mmdb", path)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()

    assert written == size
    assert peak < size // 8, f"held {peak >> 20} MiB for a {size >> 20} MiB body"


# A body decoded on the way in is a different length than the one declared, so the length
# check has to stand down rather than report a perfectly whole transfer as short.
def test_a_content_encoded_body_is_not_mistaken_for_a_short_one(
    make_client: ClientFactory,
) -> None:
    served = origin(make_client, Blob(encoding="gzip"))

    assert served.client.database.download_bytes("cdn_ip_v1", "csvgz") == SMALL

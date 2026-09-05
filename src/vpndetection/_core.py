"""Plumbing the sync and the async client both need: transport wiring, response
unwrapping, the retry policy, and the per-instance cache."""

from __future__ import annotations

import contextlib
import json
import os
import threading
from collections.abc import Awaitable, Callable, Iterator
from pathlib import Path
from typing import IO, Any, TypeVar, cast

import httpx
from cachetools import TTLCache

from ._generated.client import AuthenticatedClient, Client
from ._generated.models.download import Download
from ._generated.models.licensed_dataset import LicensedDataset
from ._generated.types import Response
from .errors import VPNDetectionError, error_from_response
from .models import Result

DEFAULT_BASE_URL = "https://api.vpndetection.io"
DEFAULT_CONCURRENCY = 8
DEFAULT_RETRIES = 2
DEFAULT_CACHE_MAX_SIZE = 10_000
DEFAULT_CACHE_TTL = 3600.0
DEFAULT_TIMEOUT = 10.0
DEFAULT_DOWNLOADS_LIMIT = 50

# One chunk of a transfer, and therefore the ceiling on what a download of any size
# costs in memory.
TRANSFER_CHUNK_BYTES = 1 << 20

_BACKOFF_BASE = 1.0

T = TypeVar("T")


def build_client(
    api_key: str | None,
    base_url: str,
    timeout: float | None,
    transport: httpx.BaseTransport | httpx.AsyncBaseTransport | None,
) -> AuthenticatedClient:
    """The generated client, wired for one of our clients.

    Every generated endpoint function types `client` as `AuthenticatedClient` because
    every operation lists a security scheme, but the lookup endpoint also accepts `{}`
    and a keyless caller must not send an empty `Authorization` header. The two classes
    are interchangeable where the endpoints use them, so the keyless one is built as
    `Client` and the cast lives here instead of at every call site.
    """
    httpx_args: dict[str, Any] = {}
    if transport is not None:
        httpx_args["transport"] = transport
    if api_key is None:
        return cast(
            AuthenticatedClient,
            Client(base_url=base_url, timeout=httpx.Timeout(timeout), httpx_args=httpx_args),
        )
    return AuthenticatedClient(
        base_url=base_url,
        token=api_key,
        timeout=httpx.Timeout(timeout),
        httpx_args=httpx_args,
    )


def build_transfer_client(
    timeout: float | None, transport: httpx.BaseTransport | None
) -> httpx.Client:
    """A SECOND client, holding no credential, for the object-storage leg of a download.

    The API answers a download with a `302` to a presigned URL, and that URL authorizes
    itself. Following the redirect on the API client would forward the key to a host
    with no business holding it, so the second request is made from here instead, where
    there is no `Authorization` header to send.

    Only the connect phase keeps the client's timeout. That timeout is a sane bound on a
    lookup and the wrong one on a body that routinely runs to gigabytes, which would
    otherwise be cut off mid-transfer. Redirects ARE followed here, unlike on the API
    client: object storage behind a CDN answers one, and there is no credential to leak
    by going along with it.
    """
    return httpx.Client(
        timeout=httpx.Timeout(None, connect=timeout),
        transport=transport,
        follow_redirects=True,
    )


def build_async_transfer_client(
    timeout: float | None, transport: httpx.AsyncBaseTransport | None
) -> httpx.AsyncClient:
    """`build_transfer_client`, for asyncio."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(None, connect=timeout),
        transport=transport,
        follow_redirects=True,
    )


def storage_refusal(res: httpx.Response) -> VPNDetectionError:
    """What object storage refusing a download link becomes.

    The body is deliberately left unread: the status is what separates a lapsed link
    from a refused one, and nothing bounds the size of an error page.
    """
    return error_from_response(
        res.status_code,
        res.headers,
        {"error": f"object storage refused the download link with status {res.status_code}"},
    )


def assert_whole_transfer(res: httpx.Response, written: int) -> None:
    """Check what arrived against what was promised.

    A transfer that dies mid-body can reach a client as a plain end of stream, and a
    short file that looks complete is worse than no file at all: the next run reads it
    as a whole dataset.

    Skipped when the body was decoded on the way in, because `Content-Length` then
    describes the ENCODED bytes and disagreeing with it is correct rather than short.
    A chunked response declares no length; httpx raises for itself when one of those is
    cut off.
    """
    declared = res.headers.get("content-length")
    encoding = res.headers.get("content-encoding", "identity").strip().lower()
    if declared is None or encoding not in ("", "identity"):
        return
    try:
        expected = int(declared)
    except ValueError:
        return
    if expected != written:
        raise VPNDetectionError(
            "network",
            f"the transfer ended after {written} of {expected} bytes",
            res.status_code,
        )


@contextlib.contextmanager
def part_file(destination: str | os.PathLike[str]) -> Iterator[IO[bytes]]:
    """A download's bytes, landing beside `destination` and moved onto it at the end.

    Two failures this prevents, and only the first is the obvious one. A transfer that
    dies half way leaves no truncated file carrying the real name. And a refresh that
    fails leaves yesterday's good copy untouched, which opening the destination itself
    could not do: that truncates it before the first byte of the new one arrives.
    """
    partial = os.fspath(destination) + ".part"
    try:
        with open(partial, "wb") as sink:
            yield sink
        os.replace(partial, destination)
    except BaseException:
        Path(partial).unlink(missing_ok=True)
        raise


def send(call: Callable[[], Response[Any]]) -> Response[Any]:
    """One generated endpoint call.

    The generated code eagerly parses the body of every DOCUMENTED status as JSON, so a
    429 or a 400 carrying an intermediary's HTML error page raises straight out of it.
    That is a failed request rather than a bug in the caller's code, so it becomes the
    one error type here.

    `KeyError` is caught for the same reason and was missed at first: the generated
    `from_dict` reads required properties by subscript, so a 200 whose body is valid
    JSON but is MISSING a required key raises `KeyError` rather than `ValueError`, and
    that reached a caller as a bare traceback instead of a typed error. Both are the
    same fault - the API said something this client cannot read.
    """
    try:
        return call()
    except (ValueError, KeyError) as exc:
        raise VPNDetectionError(
            "server_error", f"the API answered with a body this client could not read: {exc}"
        ) from exc


async def send_async(call: Callable[[], Awaitable[Response[Any]]]) -> Response[Any]:
    """`send`, awaited."""
    try:
        return await call()
    except (ValueError, KeyError) as exc:
        raise VPNDetectionError(
            "server_error", f"the API answered with a body this client could not read: {exc}"
        ) from exc


def unwrap(res: Response[Any]) -> dict[str, Any]:
    """The response body as it came off the wire, or the failure it describes."""
    body = _decode(res.content)
    status = int(res.status_code)
    if not 200 <= status < 300:
        raise error_from_response(status, _headers(res), body)
    if not isinstance(body, dict):
        raise VPNDetectionError("server_error", "the API answered with a non-object body", status)
    return body


def as_error(exc: VPNDetectionError | httpx.HTTPError) -> VPNDetectionError:
    """A transport failure, as the one error type this library raises.

    Deliberately narrow: anything else is a bug rather than a failed request, and
    turning it into a `network` error here would hide it behind a retry.
    """
    if isinstance(exc, VPNDetectionError):
        return exc
    return VPNDetectionError("network", str(exc) or type(exc).__name__)


def parse_body(body: dict[str, Any], parse: Callable[[dict[str, Any]], T]) -> T:
    """A served body through its generated model, with a malformed one reported as the
    server's failure rather than as a traceback out of the generated code."""
    try:
        return parse(body)
    except (KeyError, TypeError, ValueError) as exc:
        raise VPNDetectionError("server_error", f"malformed response from the API: {exc}") from exc


def redirect_location(res: Response[Any]) -> str:
    """Where a `302` points, or whatever the API said instead."""
    location: str | None = _headers(res).get("location")
    if int(res.status_code) == 302 and location:
        return location
    unwrap(res)
    raise VPNDetectionError(
        "server_error", "expected a redirect to object storage", int(res.status_code)
    )


def datasets_of(body: dict[str, Any]) -> list[LicensedDataset]:
    return [LicensedDataset.from_dict(d) for d in body["datasets"]]


def downloads_of(body: dict[str, Any]) -> list[Download]:
    return [Download.from_dict(d) for d in body["downloads"]]


def checksums_of(body: dict[str, Any]) -> dict[str, str]:
    return dict(body["checksums"])


def retry_delay(err: VPNDetectionError, attempt: int, retries: int) -> float | None:
    """How long to wait before attempt `attempt + 1`, or None when there must not be one.

    A server-supplied `Retry-After` wins over the backoff schedule outright: it is the
    only thing that makes a 429 worth retrying at all, so second-guessing it with a
    shorter wait would just spend the next attempt on the same rejection.
    """
    if attempt >= retries or not err.retryable:
        return None
    if err.retry_after_seconds is not None:
        return err.retry_after_seconds
    return _BACKOFF_BASE * (2.0**attempt)


class Cache:
    """A per-client result cache.

    Never global or static: two clients with different keys are on different plans and
    entitled to different fields, so a shared cache would serve one of them the other's
    shape. The lock is not optional, because the sync batch drives lookups from a thread
    pool and `TTLCache` is not thread-safe.
    """

    def __init__(self, max_size: int, ttl: float) -> None:
        self._entries: TTLCache[str, Result] = TTLCache(maxsize=max_size, ttl=ttl)
        self._lock = threading.Lock()

    def get(self, ip: str) -> Result | None:
        with self._lock:
            return self._entries.get(ip)

    def put(self, ip: str, result: Result) -> None:
        with self._lock:
            self._entries[ip] = result


# The generated Response declares a plain MutableMapping, but always carries httpx's
# case-insensitive Headers. Rebuilding one keeps a header lookup case-blind whichever it
# turns out to be, which matters for `Retry-After`.
def _headers(res: Response[Any]) -> httpx.Headers:
    return httpx.Headers(res.headers)


def _decode(content: bytes) -> Any:
    try:
        return json.loads(content)
    except ValueError:
        return None

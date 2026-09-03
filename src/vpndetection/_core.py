"""Plumbing the sync and the async client both need: transport wiring, response
unwrapping, the retry policy, and the per-instance cache."""

from __future__ import annotations

import json
import threading
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

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


def send(call: Callable[[], Response[Any]]) -> Response[Any]:
    """One generated endpoint call.

    The generated code eagerly parses the body of every DOCUMENTED status as JSON, so a
    429 or a 400 carrying an intermediary's HTML error page raises straight out of it.
    That is a failed request rather than a bug in the caller's code, so it becomes the
    one error type here.
    """
    try:
        return call()
    except ValueError as exc:
        raise VPNDetectionError(
            "server_error", f"the API answered with a body this client could not read: {exc}"
        ) from exc


async def send_async(call: Callable[[], Awaitable[Response[Any]]]) -> Response[Any]:
    """`send`, awaited."""
    try:
        return await call()
    except ValueError as exc:
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

"""The framework-agnostic half of a web middleware.

An adapter - vpndetection-django, vpndetection-flask, vpndetection-fastapi - keeps
only the parts that are genuinely framework-shaped and shares everything here, so the
shared conformance corpus is asserted once for Python rather than once per framework.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, Literal, TypeVar

from .._core import DEFAULT_BASE_URL, check_timeout
from ..aio import AsyncVPNDetection
from ..bogon import is_bogon
from ..client import VPNDetection
from ..errors import VPNDetectionError
from ..models import Result
from .condition import Conditions, matches, missing_members, validate

__all__ = [
    "AsyncCore",
    "Core",
    "IpSelector",
    "Lookup",
    "Options",
    "RequestView",
    "Selectors",
    "bind_selectors",
]

Req = TypeVar("Req")

#: How the client address is decided.
#:
#: There is no portable answer: a framework's own accessor may return the socket peer,
#: or may already have walked a proxy chain, depending on the framework and on how the
#: application configured it. You know your framework and your edge, so this is yours
#: to choose.
IpSelector = Callable[[Req], "str | None"]

#: What to do when a condition names a member the plan does not serve.
MissingFieldAction = Literal["warn", "raise", "ignore"]

_log = logging.getLogger("vpndetection")

# Defaults set for a request path rather than for a script: failing open quickly beats
# holding a visitor while we try again.
DEFAULT_TIMEOUT = 2.5
DEFAULT_RETRIES = 0


@dataclass(frozen=True, slots=True)
class RequestView:
    """Enough of an incoming request for a selector to work with, whatever framework it
    came from. An adapter supplies one of these per request."""

    #: A request header by name, case-insensitively.
    header: Callable[[str], str | None]
    #: The framework's own client-address accessor, whatever that resolves to here.
    framework_ip: Callable[[], str | None]


@dataclass(frozen=True, slots=True)
class Lookup:
    """What a middleware attached to the request, whether or not it succeeded."""

    #: Whether the condition matched. Always False when no condition was configured.
    blocked: bool
    #: The address that was classified, as the selector resolved it.
    ip: str | None = None
    #: The answer. None when the lookup failed.
    result: Result | None = None
    #: Why the lookup failed. None when it succeeded.
    error: Exception | None = None


@dataclass(slots=True)
class Options(Generic[Req]):
    """How a middleware behaves. Everything is optional except that you almost
    certainly want an api_key: the free allowance is counted per source address, and a
    server is one source address."""

    #: An existing client to use. Prefer this if you already hold one: two clients mean
    #: two caches, and a cache is per instance because two keys can be on different
    #: plans and entitled to different fields.
    client: VPNDetection | AsyncVPNDetection | None = None
    api_key: str | None = None
    base_url: str | None = None
    #: How long a lookup may hold the request, in seconds. Defaults to 2.5, a much
    #: tighter bound than a client's own. Applied to each lookup rather than to the
    #: client, so it holds for a ``client`` you pass in without changing that client's
    #: timeout for anything else it does. Anything that is not a finite number above
    #: 0 is a ``ValueError`` when the middleware is built.
    timeout: float = DEFAULT_TIMEOUT
    #: Retry attempts for a transient failure. Defaults to 0, unlike the client's 2.
    retries: int = DEFAULT_RETRIES
    #: How the client address is decided. Defaults to the framework's own accessor.
    ip_selector: IpSelector[Req] | None = None
    #: What to block on. Leave it None to only enrich the request and leave the
    #: decision to your own code.
    block_condition: Conditions | None = None
    #: Block when the lookup itself fails. Defaults to False, so our outage does not
    #: become yours.
    fail_closed: bool = False
    #: What to do when the condition names a member your plan does not serve.
    on_missing_field: MissingFieldAction = "warn"
    #: Skip classification for this request entirely.
    skip: Callable[[Req], bool] | None = None
    #: Where warnings go. Defaults to the "vpndetection" logger.
    on_warn: Callable[[str], None] | None = None
    _warned: set[str] = field(default_factory=set, repr=False)


class _Base(Generic[Req]):
    def __init__(self, options: Options[Req], default_ip_selector: IpSelector[Req]) -> None:
        validate(options.block_condition)
        check_timeout(options.timeout)
        self._options = options
        self._condition = options.block_condition
        self._selector = options.ip_selector or default_ip_selector
        self._warned: set[str] = set()

    @property
    def blocking(self) -> bool:
        """Whether a condition was configured at all."""
        return self._condition is not None

    # A misconfiguration is the same on every request, so saying so once is a warning
    # and saying so a million times is an outage of its own.
    def _warn(self, message: str) -> None:
        if message in self._warned:
            return
        self._warned.add(message)
        if self._options.on_warn is not None:
            self._options.on_warn(message)
        else:
            _log.warning("%s", message)

    def _resolve(self, request: Req) -> str | Lookup:
        ip = (self._selector(request) or "").strip()
        if not ip:
            self._warn(
                "could not resolve a client address from this request; pass an "
                "ip_selector that knows where yours comes from"
            )
            return Lookup(
                blocked=self._options.fail_closed,
                error=VPNDetectionError("bad_request", "no client address on the request"),
            )
        if is_bogon(ip):
            # Expected in local development. Anywhere else it means a proxy sits in
            # front and its own address is what reached us.
            self._warn(
                f"resolved the client address as {ip}, which is not a public address. "
                "If this application runs behind a proxy or load balancer, configure "
                "its trusted-proxy setting or pass an ip_selector that reads your "
                "edge's header."
            )
        return ip

    def _decide(self, ip: str, result: Result) -> Lookup:
        if self._condition is not None:
            self._report_missing(result)
        return Lookup(
            blocked=self._condition is not None and matches(self._condition, result),
            ip=ip,
            result=result,
        )

    def _failed(self, ip: str, error: Exception) -> Lookup:
        return Lookup(blocked=self._options.fail_closed, ip=ip, error=error)

    def _report_missing(self, result: Result) -> None:
        if self._options.on_missing_field == "ignore" or self._condition is None:
            return
        missing = missing_members(self._condition, result)
        if not missing:
            return
        message = (
            f"block_condition names {', '.join(missing)}, which your plan does not "
            'include, so those terms can never match. An absent member means "not in '
            'your plan", not "checked, and no".'
        )
        if self._options.on_missing_field == "raise":
            raise ValueError(f"vpndetection: {message}")
        self._warn(message)


class Core(_Base[Req]):
    """Resolve an address, classify it, and decide whether the condition matched.

    For a WSGI framework - Django, Flask - where the request path is synchronous.
    """

    def __init__(self, options: Options[Req], default_ip_selector: IpSelector[Req]) -> None:
        super().__init__(options, default_ip_selector)
        client = options.client
        if client is None:
            client = VPNDetection(
                api_key=options.api_key, base_url=options.base_url or DEFAULT_BASE_URL
            )
        if isinstance(client, AsyncVPNDetection):
            raise TypeError("Core needs a VPNDetection; use AsyncCore for an async client")
        self._client = client

    def evaluate(self, request: Req) -> Lookup | None:
        """Classify one request. Answers None when skip claimed it."""
        if self._options.skip is not None and self._options.skip(request):
            return None
        resolved = self._resolve(request)
        if isinstance(resolved, Lookup):
            return resolved
        try:
            result = self._client.lookup(
                resolved, retries=self._options.retries, timeout=self._options.timeout
            )
        except Exception as error:  # noqa: BLE001 - a failed lookup must never propagate
            return self._failed(resolved, error)
        return self._decide(resolved, result)


class AsyncCore(_Base[Req]):
    """The same, for an ASGI framework - FastAPI, Starlette, Litestar."""

    def __init__(self, options: Options[Req], default_ip_selector: IpSelector[Req]) -> None:
        super().__init__(options, default_ip_selector)
        client = options.client
        if client is None:
            client = AsyncVPNDetection(
                api_key=options.api_key, base_url=options.base_url or DEFAULT_BASE_URL
            )
        if not isinstance(client, AsyncVPNDetection):
            raise TypeError("AsyncCore needs an AsyncVPNDetection; use Core for a sync client")
        self._client = client

    async def evaluate(self, request: Req) -> Lookup | None:
        """Classify one request. Answers None when skip claimed it."""
        if self._options.skip is not None and self._options.skip(request):
            return None
        resolved = self._resolve(request)
        if isinstance(resolved, Lookup):
            return resolved
        try:
            result = await self._client.lookup(
                resolved, retries=self._options.retries, timeout=self._options.timeout
            )
        except Exception as error:  # noqa: BLE001 - a failed lookup must never propagate
            return self._failed(resolved, error)
        return self._decide(resolved, result)


@dataclass(frozen=True, slots=True)
class Selectors(Generic[Req]):
    """The shared selectors, bound to one framework's request type."""

    #: The framework's own client-address accessor. What that resolves to depends on
    #: the framework and on how you configured it.
    default: IpSelector[Req]
    #: An address from ``X-Forwarded-For``.
    #:
    #: The LEFT-MOST entry is whatever the caller sent, because proxies append, so a
    #: visitor who sets the header themselves appears first and this returns their
    #: forgery. It is only trustworthy when an edge you control overwrites the header.
    #: When you know how many proxies sit in front, count from the right with ``depth``:
    #: 1 is the address your nearest proxy saw.
    xff: Callable[..., IpSelector[Req]]
    #: An address from a single-value header, for an edge that writes one -
    #: ``header("CF-Connecting-IP")`` behind Cloudflare. Falls back to the framework's
    #: accessor when the header is absent.
    header: Callable[[str], IpSelector[Req]]


def bind_selectors(view: Callable[[Req], RequestView]) -> Selectors[Req]:
    """Give an adapter the shared selectors under its own request type.

    The adapter passes a function exposing its request once, so a caller writing a
    custom selector still works with the object they know.
    """

    def default(request: Req) -> str | None:
        return view(request).framework_ip()

    def xff(depth: int = 0) -> IpSelector[Req]:
        def select(request: Req) -> str | None:
            seen = view(request)
            raw = seen.header("X-Forwarded-For") or ""
            chain = [entry.strip() for entry in raw.split(",") if entry.strip()]
            if not chain:
                return seen.framework_ip()
            if depth <= 0 or depth > len(chain):
                return chain[0]
            return chain[-depth]

        return select

    def header(name: str) -> IpSelector[Req]:
        def select(request: Req) -> str | None:
            seen = view(request)
            value = (seen.header(name) or "").strip()
            return value or seen.framework_ip()

        return select

    return Selectors(default=default, xff=xff, header=header)

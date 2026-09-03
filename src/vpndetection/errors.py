"""The one exception this library raises, and how a response becomes one."""

from __future__ import annotations

import datetime
import email.utils
import math
from typing import Any, Literal

import httpx

__all__ = ["ErrorKind", "VPNDetectionError"]

ErrorKind = Literal[
    "bad_request",
    "unauthorized",
    "forbidden",
    "rate_limited",
    "quota_exceeded",
    "server_error",
    "network",
]
"""Why a request failed.

`rate_limited` and `quota_exceeded` both arrive as HTTP 429 and are NOT the same thing.
A rate limit is the API protecting itself and carries `Retry-After`; retrying works. A
spent quota carries no such header and retrying will not help until the window rolls
over or the limit is raised. The header is the only thing that distinguishes them.
"""

_RETRYABLE: frozenset[str] = frozenset({"rate_limited", "server_error", "network"})


class VPNDetectionError(Exception):
    """Every failure this library reports, discriminated by `kind`."""

    kind: ErrorKind
    status: int | None
    retry_after_seconds: float | None

    def __init__(
        self,
        kind: ErrorKind,
        message: str,
        status: int | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.status = status
        self.retry_after_seconds = retry_after_seconds

    @property
    def message(self) -> str:
        return str(self)

    @property
    def retryable(self) -> bool:
        """Whether retrying this exact request could succeed."""
        return self.kind in _RETRYABLE

    def __repr__(self) -> str:
        return (
            f"VPNDetectionError(kind={self.kind!r}, status={self.status!r}, message={str(self)!r})"
        )


def error_from_response(status: int, headers: httpx.Headers, body: Any) -> VPNDetectionError:
    message = _message_of(body) or f"request failed with status {status}"
    retry_after = _parse_retry_after(headers.get("retry-after"))

    if status == 429:
        # Present means transient, absent means an allowance is spent. Nothing else in
        # the response separates the two.
        if retry_after is None:
            return VPNDetectionError("quota_exceeded", message, status)
        return VPNDetectionError("rate_limited", message, status, retry_after)
    if status == 400:
        return VPNDetectionError("bad_request", message, status)
    if status == 401:
        return VPNDetectionError("unauthorized", message, status)
    if status == 403:
        return VPNDetectionError("forbidden", message, status)
    if status == 404:
        return VPNDetectionError("bad_request", message, status)
    return VPNDetectionError("server_error", message, status)


# The two APIs behind this host answer with different envelopes: the lookup endpoint
# uses `error`, the database endpoints use `rc`. Both are read here so a caller never
# has to know which one they hit.
def _message_of(body: Any) -> str | None:
    if not isinstance(body, dict):
        return None
    for key in ("error", "rc"):
        value = body.get(key)
        if isinstance(value, str) and value != "":
            return value
    return None


def _parse_retry_after(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    try:
        seconds = float(value)
    except ValueError:
        pass
    else:
        return seconds if seconds >= 0 else None
    # The header also permits an HTTP date.
    try:
        when = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=datetime.UTC)
    delta = (when - datetime.datetime.now(datetime.UTC)).total_seconds()
    return max(0.0, math.ceil(delta))

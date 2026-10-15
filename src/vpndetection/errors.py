"""The one exception this library raises, and how a response becomes one."""

from __future__ import annotations

import datetime
import math
import re
from typing import Any, Literal

import httpx

__all__ = [
    "ErrorKind",
    "OauthAccessDeniedError",
    "OauthError",
    "OauthExpiredTokenError",
    "VPNDetectionError",
]

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
            f"{type(self).__name__}(kind={self.kind!r}, status={self.status!r}, "
            f"message={str(self)!r})"
        )


class OauthError(VPNDetectionError):
    """The authorization server refusing an OAuth request, such as `slow_down` or
    `invalid_grant`. Never retryable: every token exchange spends what it presents.

    Its `kind` follows the status like any response's, so a 401 here is `unauthorized` and
    means an unregistered `client_id`, never the API key, which these requests do not carry.
    """

    error_code: str
    """The server's code, kept as sent."""
    error_description: str | None
    """The server's explanation, when it sent one."""

    def __init__(
        self, error_code: str, error_description: str | None = None, status: int | None = None
    ) -> None:
        kind = (
            "bad_request" if status is None else error_from_response(status, _NO_HEADERS, None).kind
        )
        message = error_code if error_description is None else f"{error_code}: {error_description}"
        super().__init__(kind, message, status)
        self.error_code = error_code
        self.error_description = error_description

    @property
    def retryable(self) -> bool:
        return False


class OauthAccessDeniedError(OauthError):
    """The person refused the sign-in. Its device code is spent, so a new attempt starts over."""

    def __init__(self, error_description: str | None = None, status: int | None = None) -> None:
        super().__init__("access_denied", error_description, status)


class OauthExpiredTokenError(OauthError):
    """The device code is no longer valid: it expired, or was already used or refused. A poll
    that outlives the code raises this itself, with a `status` of None."""

    def __init__(self, error_description: str | None = None, status: int | None = None) -> None:
        super().__init__("expired_token", error_description, status)


def oauth_error_from(error_code: str, error_description: str | None, status: int) -> OauthError:
    if error_code == "access_denied":
        return OauthAccessDeniedError(error_description, status)
    if error_code == "expired_token":
        return OauthExpiredTokenError(error_description, status)
    return OauthError(error_code, error_description, status)


def error_from_response(status: int, headers: httpx.Headers, body: Any) -> VPNDetectionError:
    message = _message_of(body) or f"request failed with status {status}"
    retry_after = _parse_retry_after(headers.get("retry-after"))

    if status == 429:
        # Present means transient, absent means an allowance is spent. Nothing else in
        # the response separates the two.
        if retry_after is None:
            return VPNDetectionError("quota_exceeded", message, status)
        return VPNDetectionError("rate_limited", message, status, retry_after)
    if status == 401:
        return VPNDetectionError("unauthorized", message, status)
    if status == 403:
        return VPNDetectionError("forbidden", message, status)
    # Every other 4xx on the RANGE rather than a list, so a status nobody enumerated is
    # still the caller's error and is never retried as if the server had failed.
    if 400 <= status < 500:
        return VPNDetectionError("bad_request", message, status)
    return VPNDetectionError("server_error", message, status)


_NO_HEADERS = httpx.Headers()


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


# `Retry-After` is a count of seconds or an HTTP date in one of RFC 9110's three forms,
# always GMT, and nothing else: `float()` also read `+1`, `1_0`, `1e3` and `1.5` as counts,
# and `email.utils` read a date in any zone, without its day name or with a two-digit year,
# so `1_0` held a call ten seconds and a `PST` date eight hours (5.7.1, measured 2026-10-15).
_SECONDS = re.compile(r"[0-9]+")
_MONTH = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
_CLOCK = r"([0-9]{2}):([0-9]{2}):([0-9]{2})"
_IMF_FIXDATE = re.compile(
    rf"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), ([0-9]{{2}}) {_MONTH} ([0-9]{{4}}) {_CLOCK} GMT"
)
_RFC850_DATE = re.compile(
    rf"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), ([0-9]{{2}})-{_MONTH}-([0-9]{{2}}) {_CLOCK} GMT"
)
_ASCTIME_DATE = re.compile(
    rf"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) {_MONTH} ([0-9]{{2}}| [0-9]) {_CLOCK} ([0-9]{{4}})"
)
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip(" \t")
    if _SECONDS.fullmatch(value):
        # A count of any length: float() reads one past its range as inf, never raising.
        return float(value)
    when = _http_date(value)
    if when is None:
        return None
    delta = (when - datetime.datetime.now(datetime.UTC)).total_seconds()
    return max(0.0, math.ceil(delta))


# The moment an HTTP date names, or None for anything else, a day no calendar has included.
def _http_date(value: str) -> datetime.datetime | None:
    if match := _IMF_FIXDATE.fullmatch(value):
        day, month, year, hour, minute, second = match.groups()
        full_year = int(year)
    elif match := _RFC850_DATE.fullmatch(value):
        day, month, year, hour, minute, second = match.groups()
        # RFC 9110: a two-digit year more than 50 years ahead is the most recent past one.
        this_year = datetime.datetime.now(datetime.UTC).year
        full_year = this_year - this_year % 100 + int(year)
        if full_year > this_year + 50:
            full_year -= 100
    elif match := _ASCTIME_DATE.fullmatch(value):
        month, day, hour, minute, second, year = match.groups()
        full_year = int(year)
    else:
        return None
    try:
        return datetime.datetime(
            full_year,
            _MONTHS.index(month) + 1,
            int(day),
            int(hour),
            int(minute),
            int(second),
            tzinfo=datetime.UTC,
        )
    except ValueError:
        return None

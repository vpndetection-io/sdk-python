"""What a lookup answers, and the one place the wire shape becomes an idiomatic one."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Literal, TypeVar

from ._generated.models.lookup_response import LookupResponse
from ._generated.types import Unset

__all__ = [
    "ClassDetail",
    "Flag",
    "Format",
    "ProxyDetail",
    "Result",
    "VpnDetail",
]

Flag = Literal[
    "is_vpn",
    "is_hosting",
    "is_relay",
    "is_tor",
    "is_cdn",
    "is_resproxy",
    "is_dcproxy",
    "is_mobproxy",
]

Format = Literal["csvgz", "mmdb"]


@dataclass(frozen=True, slots=True)
class VpnDetail:
    """What is known about the VPN attribution.

    Every field is populated when the object itself is, empty values included;
    `confidence` and `method` are max only, so on a lower plan they are `None` on an
    otherwise populated object.
    """

    provider: str | None = None
    last_seen: datetime.date | None = None
    confidence: str | None = None
    method: str | None = None


@dataclass(frozen=True, slots=True)
class ClassDetail:
    """The shared detail shape for the hosting, relay, tor and cdn datasets."""

    provider: str | None = None
    confidence: str | None = None
    last_seen: datetime.date | None = None


@dataclass(frozen=True, slots=True)
class ProxyDetail:
    """The shared detail shape for the residential, datacenter and mobile proxy
    families, measured over a rolling 90 day window."""

    provider: str | None = None
    first_seen: datetime.date | None = None
    last_seen: datetime.date | None = None
    hits: int | None = None
    hits_days_pct: int | None = None
    providers_num: int | None = None


@dataclass(frozen=True, slots=True)
class Result:
    """What a lookup answers.

    An **optional** member is one your plan does not include. It never means "we could
    not check", so `None` and `False` are genuinely different answers: `None` is "not in
    your plan", `False` is "checked, and no". Use `flagged()` when you only care whether
    the address is flagged.

    A detail object that is present but empty (every field `None`) means the flag above
    it is false. A populated one always carries every one of its keys.

    Frozen, because a cached answer is handed to every later caller of the same address.
    """

    ip: str
    is_vpn: bool
    is_bogon: bool = False

    is_hosting: bool | None = None
    is_relay: bool | None = None
    is_tor: bool | None = None
    is_cdn: bool | None = None
    is_resproxy: bool | None = None
    is_dcproxy: bool | None = None
    is_mobproxy: bool | None = None

    vpn: VpnDetail | None = None
    hosting: ClassDetail | None = None
    relay: ClassDetail | None = None
    tor: ClassDetail | None = None
    cdn: ClassDetail | None = None
    resproxy: ProxyDetail | None = None
    dcproxy: ProxyDetail | None = None
    mobproxy: ProxyDetail | None = None

    raw: dict[str, Any] = field(default_factory=dict)

    def flagged(self, flag: Flag) -> bool:
        """Whether a flag is present AND true, with anything your plan does not include
        reading as false.

        Python has no `??`, and `result.is_hosting` is three-valued, so every caller who
        only wants a yes-or-no would otherwise write the same coalesce by hand.
        """
        return getattr(self, flag) is True


def to_result(body: dict[str, Any]) -> Result:
    """Turn one served answer into a `Result`.

    The generated model marks a field your plan does not include with its own `UNSET`
    sentinel; this is the single place that becomes `None`, so no consumer ever has to
    know the sentinel exists. Every field is read on PRESENCE rather than truthiness, or
    a plan that includes a field and answers `false` would lose it.
    """
    parsed = LookupResponse.from_dict(body)
    return Result(
        ip=parsed.ip,
        is_vpn=parsed.is_vpn,
        is_bogon=False,
        is_hosting=_opt(parsed.is_hosting),
        is_relay=_opt(parsed.is_relay),
        is_tor=_opt(parsed.is_tor),
        is_cdn=_opt(parsed.is_cdn),
        is_resproxy=_opt(parsed.is_resproxy),
        is_dcproxy=_opt(parsed.is_dcproxy),
        is_mobproxy=_opt(parsed.is_mobproxy),
        vpn=_vpn(parsed.vpn),
        hosting=_class(parsed.hosting),
        relay=_class(parsed.relay),
        tor=_class(parsed.tor),
        cdn=_class(parsed.cdn),
        resproxy=_proxy(parsed.resproxy),
        dcproxy=_proxy(parsed.dcproxy),
        mobproxy=_proxy(parsed.mobproxy),
        raw=body,
    )


T = TypeVar("T")


def _opt(value: T | Unset) -> T | None:
    return None if isinstance(value, Unset) else value


def _vpn(value: Any) -> VpnDetail | None:
    if isinstance(value, Unset):
        return None
    return VpnDetail(
        provider=_opt(value.provider),
        last_seen=_opt(value.last_seen),
        confidence=_opt(value.confidence),
        method=_opt(value.method),
    )


def _class(value: Any) -> ClassDetail | None:
    if isinstance(value, Unset):
        return None
    return ClassDetail(
        provider=_opt(value.provider),
        confidence=_opt(value.confidence),
        last_seen=_opt(value.last_seen),
    )


def _proxy(value: Any) -> ProxyDetail | None:
    if isinstance(value, Unset):
        return None
    return ProxyDetail(
        provider=_opt(value.provider),
        first_seen=_opt(value.first_seen),
        last_seen=_opt(value.last_seen),
        hits=_opt(value.hits),
        hits_days_pct=_opt(value.hits_days_pct),
        providers_num=_opt(value.providers_num),
    )

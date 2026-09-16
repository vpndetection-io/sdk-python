"""What the API answers, and the one place the wire shape becomes an idiomatic one."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Literal, TypeVar

from ._generated.models.lookup_response import LookupResponse
from ._generated.types import Unset
from .errors import VPNDetectionError

__all__ = [
    "ClassDetail",
    "DeviceAuthorization",
    "Flag",
    "Format",
    "OauthMetadata",
    "ProxyDetail",
    "Result",
    "TokenResponse",
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


@dataclass(frozen=True, slots=True)
class OauthMetadata:
    """The authorization server's discovery document (RFC 8414)."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    device_authorization_endpoint: str | None = None
    revocation_endpoint: str | None = None
    scopes_supported: tuple[str, ...] | None = None
    response_types_supported: tuple[str, ...] | None = None
    grant_types_supported: tuple[str, ...] | None = None
    code_challenge_methods_supported: tuple[str, ...] | None = None
    token_endpoint_auth_methods_supported: tuple[str, ...] | None = None
    authorization_response_iss_parameter_supported: bool | None = None
    service_documentation: str | None = None


@dataclass(frozen=True, slots=True)
class DeviceAuthorization:
    """A started device sign-in. Show the person `verification_uri` and `user_code`, then
    pass this to `poll_device_token`. `expires_in` and `interval` are seconds.

    `device_code` is left out of the repr, because it is what redeems the sign-in.
    """

    device_code: str = field(repr=False)
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    verification_uri_complete: str | None = None


@dataclass(frozen=True, slots=True)
class TokenResponse:
    """What a token exchange answers.

    `apikey_id` names the API key the person picked, and `apikey` is its secret. Either can
    be None: no key was picked, or their role no longer reveals keys. `apikey` also stays
    None after a refresh, which never hands a secret over, and for a key created before
    secrets could be revealed. The secrets are left out of the repr, so logging one does
    not leak them.
    """

    access_token: str = field(repr=False)
    token_type: str
    expires_in: int
    refresh_token: str | None = field(default=None, repr=False)
    scope: str | None = None
    apikey_id: str | None = None
    apikey: str | None = field(default=None, repr=False)


def to_oauth_metadata(body: Any, status: int) -> OauthMetadata:
    return OauthMetadata(**_members(body, _OAUTH_METADATA, status))


def to_device_authorization(body: Any, status: int) -> DeviceAuthorization:
    return DeviceAuthorization(**_members(body, _DEVICE_AUTHORIZATION, status))


def to_token_response(body: Any, status: int) -> TokenResponse:
    return TokenResponse(**_members(body, _TOKEN_RESPONSE, status))


# A member's type on the wire, and whether a 2xx without it is malformed.
_Member = tuple[Literal["str", "int", "bool", "strs"], bool]

_OAUTH_METADATA: dict[str, _Member] = {
    "issuer": ("str", True),
    "authorization_endpoint": ("str", True),
    "token_endpoint": ("str", True),
    "device_authorization_endpoint": ("str", False),
    "revocation_endpoint": ("str", False),
    "scopes_supported": ("strs", False),
    "response_types_supported": ("strs", False),
    "grant_types_supported": ("strs", False),
    "code_challenge_methods_supported": ("strs", False),
    "token_endpoint_auth_methods_supported": ("strs", False),
    "authorization_response_iss_parameter_supported": ("bool", False),
    "service_documentation": ("str", False),
}

_DEVICE_AUTHORIZATION: dict[str, _Member] = {
    "device_code": ("str", True),
    "user_code": ("str", True),
    "verification_uri": ("str", True),
    "verification_uri_complete": ("str", False),
    "expires_in": ("int", True),
    "interval": ("int", True),
}

_TOKEN_RESPONSE: dict[str, _Member] = {
    "access_token": ("str", True),
    "token_type": ("str", True),
    "expires_in": ("int", True),
    "refresh_token": ("str", False),
    "scope": ("str", False),
    "apikey_id": ("str", False),
    "apikey": ("str", False),
}

_WIRE_NAMES = {"apikey_id": "mslm:apikey_id", "apikey": "mslm:apikey"}


# Only the declared members are copied, on PRESENCE, so an absent one stays None and an
# empty `scope` stays "". A null reads as absent. Anything undeclared is dropped.
def _members(body: Any, members: dict[str, _Member], status: int) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise VPNDetectionError("server_error", "the answer was not a JSON object", status)
    out: dict[str, Any] = {}
    for name, (kind, required) in members.items():
        wire = _WIRE_NAMES.get(name, name)
        value = body.get(wire)
        if value is None:
            if required:
                raise VPNDetectionError("server_error", f"the answer carried no {wire}", status)
            continue
        out[name] = _typed(value, kind, wire, status)
    return out


def _typed(value: Any, kind: str, wire: str, status: int) -> Any:
    if kind == "strs" and isinstance(value, list) and all(isinstance(v, str) for v in value):
        return tuple(value)
    if kind == "str" and isinstance(value, str):
        return value
    if kind == "bool" and isinstance(value, bool):
        return value
    # bool is an int in Python, and never a count of seconds.
    if kind == "int" and isinstance(value, int) and not isinstance(value, bool):
        return value
    if kind == "int" and isinstance(value, float) and value.is_integer():
        return int(value)
    raise VPNDetectionError("server_error", f"the answer's {wire} is not a {kind}", status)

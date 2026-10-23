"""What the API answers, and the one place the wire shape becomes an idiomatic one."""

from __future__ import annotations

import datetime
import enum
import sys
import types
import typing
from dataclasses import dataclass, field
from typing import Any, Literal, TypeVar, get_args

from ._generated import models as _generated_models
from ._generated.models.database_license_type_type_1 import DatabaseLicenseTypeType1
from ._generated.models.lookup_response import LookupResponse
from ._generated.models.standing import Standing
from ._generated.types import Unset
from .errors import VPNDetectionError

__all__ = [
    "DATABASE_FORMATS",
    "LICENSE_TYPES",
    "STANDINGS",
    "ClassDetail",
    "DeviceAuthorization",
    "Flag",
    "Format",
    "OauthMetadata",
    "ProxyDetail",
    "PubproxyDetail",
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
    "is_pubproxy",
]

Format = Literal["csvgz", "mmdb"]

DATABASE_FORMATS: tuple[Format, ...] = get_args(Format)
"""Every `Format`, at runtime.

A `Literal` is erased to nothing a program can check against, so a format read from a flag,
a form or a config file has these to be tested against before a call.
"""

STANDINGS: tuple[str, ...] = tuple(member.value for member in Standing)
"""Every `standing` a database family can carry, at runtime, read off the pinned spec."""

LICENSE_TYPES: tuple[str, ...] = tuple(member.value for member in DatabaseLicenseTypeType1)
"""Every `license_type`, at runtime, read off the pinned spec. `None`, for no license, is not
one of them."""


@dataclass(frozen=True, slots=True)
class VpnDetail:
    """What is known about the VPN attribution.

    Every field is populated when the object itself is, empty values included.
    `method` is deprecated: no plan is answered with it since 2026-10-20, so it is
    `None`; read `confidence` instead. It stays until the next major.
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
class PubproxyDetail:
    """The address in Public Proxy IP, open proxies anyone can connect through, over a
    rolling 90 day window. It covers both ends of a proxy: the address it listens on
    (`entry`) and the address its traffic leaves from (`exit`).

    `protocols` is empty where only the address is known, and `last_usable` is the
    empty string when no request through a proxy on the address was answered.
    `num_ports` counts the ports a proxy listens on here (0 when it is only an exit),
    and `num_proxies` the proxies whose traffic left from here (0 when it is only an
    entry).
    """

    entry: bool | None = None
    exit: bool | None = None
    protocols: tuple[str, ...] | None = None
    num_ports: int | None = None
    num_proxies: int | None = None
    last_seen: datetime.date | None = None
    last_usable: str | None = None


@dataclass(frozen=True, slots=True)
class Location:
    """Where the address is, on every keyed answer.

    Every field is set whenever the object is, an empty string where it is not known.
    """

    continent: str = ""
    continent_name: str = ""
    country: str = ""
    country_name: str = ""
    timezone: str = ""
    currency_code: str = ""
    currency_name: str = ""
    currency_symbol: str = ""
    flag_emoji: str = ""
    flag_unicode: str = ""


@dataclass(frozen=True, slots=True)
class Asn:
    """The AS announcing the address, on every keyed answer: `asn` is 0 where none does."""

    asn: int = 0
    name: str = ""
    domain: str = ""
    type: str = ""
    prefix: str = ""


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
    is_pubproxy: bool | None = None

    vpn: VpnDetail | None = None
    hosting: ClassDetail | None = None
    relay: ClassDetail | None = None
    tor: ClassDetail | None = None
    cdn: ClassDetail | None = None
    resproxy: ProxyDetail | None = None
    dcproxy: ProxyDetail | None = None
    mobproxy: ProxyDetail | None = None
    pubproxy: PubproxyDetail | None = None

    location: Location | None = None
    asn: Asn | None = None

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
    check_answer(parsed)
    # The generated model takes any value it finds, so `"ip": null` or `"is_vpn": "yes"`
    # came back as the answer, from a lookup and a batch entry alike (5.7.1, measured
    # 2026-10-15). Each is the server's failure, raised for the caller to report as one.
    if not isinstance(parsed.ip, str) or parsed.ip == "":
        raise TypeError(f"the answer's ip is not an address: {parsed.ip!r}")
    for flag in _FLAGS:
        value = getattr(parsed, flag)
        if not isinstance(value, bool) and not (
            flag != "is_vpn" and isinstance(value, Unset | None)
        ):
            raise TypeError(f"the answer's {flag} is not a boolean: {value!r}")
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
        is_pubproxy=_opt(parsed.is_pubproxy),
        vpn=_vpn(parsed.vpn),
        hosting=_class(parsed.hosting),
        relay=_class(parsed.relay),
        tor=_class(parsed.tor),
        cdn=_class(parsed.cdn),
        resproxy=_proxy(parsed.resproxy),
        dcproxy=_proxy(parsed.dcproxy),
        mobproxy=_proxy(parsed.mobproxy),
        pubproxy=_pubproxy(parsed.pubproxy),
        location=_location(parsed.location),
        asn=_asn(parsed.asn),
        raw=body,
    )


def check_answer(value: Any) -> None:
    """Raises TypeError where a generated model holds a member of another type than the
    spec gives it, or None in one the spec requires and never sends as null, at any depth.

    `from_dict` takes a scalar as it comes and reads a required member by subscript, so
    `"version": "3"`, an `entries` or `bytes` of `"760"`, `"open": "yes"` and a lookup's
    `dcproxy.hits` of `"3"` came back as the answer, and so did a required member sent as
    null (5.11.0 and 5.7.1, measured 2026-10-22 and -15). A bool never stands for a
    number, while an int stands for a float, which JSON does not tell apart.
    """
    if isinstance(value, list | tuple):
        for item in value:
            check_answer(item)
        return
    if isinstance(value, dict):
        for item in value.values():
            check_answer(item)
        return
    fields = getattr(type(value), "__attrs_attrs__", None)
    if fields is None:
        return
    hints = _hints(type(value))
    for member_field in fields:
        member = getattr(value, member_field.name)
        hint = hints.get(member_field.name, Any)
        if member is None:
            # An optional member sent as null reads as absent.
            if not _conforms(None, hint) and Unset not in typing.get_args(hint):
                raise TypeError(f"{type(value).__name__}.{member_field.name} is null")
            continue
        if not _conforms(member, hint):
            raise TypeError(f"{type(value).__name__}.{member_field.name} is not {hint}: {member!r}")
        check_answer(member)


_HINTS: dict[type, dict[str, Any]] = {}


def _hints(model: type) -> dict[str, Any]:
    """A generated model's member types, its string annotations resolved: each module
    imports the models it names only for type checking, so they come from the package."""
    hints = _HINTS.get(model)
    if hints is None:
        namespace = dict(vars(_generated_models))
        namespace.update(vars(sys.modules[model.__module__]))
        hints = _HINTS[model] = typing.get_type_hints(model, globalns=namespace)
    return hints


def _conforms(value: Any, hint: Any) -> bool:
    if hint is Any:
        return True
    origin = typing.get_origin(hint)
    if origin is typing.Union or origin is types.UnionType:
        return any(_conforms(value, arm) for arm in typing.get_args(hint))
    if hint is type(None):
        return value is None
    if origin in (list, tuple):
        arms = typing.get_args(hint)
        return isinstance(value, list | tuple) and (
            not arms or all(_conforms(item, arms[0]) for item in value)
        )
    if origin is dict:
        arms = typing.get_args(hint)
        return isinstance(value, dict) and (
            len(arms) < 2 or all(_conforms(item, arms[1]) for item in value.values())
        )
    if hint is bool:
        return isinstance(value, bool)
    if hint is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if hint is float:
        return isinstance(value, int | float) and not isinstance(value, bool)
    if isinstance(hint, type) and (
        hint in (str, datetime.date, datetime.datetime)
        or issubclass(hint, enum.Enum)
        or hasattr(hint, "__attrs_attrs__")
        or hint is Unset
    ):
        return isinstance(value, hint)
    return True


# The flags a lookup answers, `is_vpn` the one every plan serves.
_FLAGS = (
    "is_vpn",
    "is_hosting",
    "is_relay",
    "is_tor",
    "is_cdn",
    "is_resproxy",
    "is_dcproxy",
    "is_mobproxy",
    "is_pubproxy",
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


def _location(value: Any) -> Location | None:
    if isinstance(value, Unset):
        return None
    return Location(
        continent=value.continent,
        continent_name=value.continent_name,
        country=value.country,
        country_name=value.country_name,
        timezone=value.timezone,
        currency_code=value.currency_code,
        currency_name=value.currency_name,
        currency_symbol=value.currency_symbol,
        flag_emoji=value.flag_emoji,
        flag_unicode=value.flag_unicode,
    )


def _asn(value: Any) -> Asn | None:
    if isinstance(value, Unset):
        return None
    return Asn(
        asn=value.asn, name=value.name, domain=value.domain, type=value.type_, prefix=value.prefix
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


def _pubproxy(value: Any) -> PubproxyDetail | None:
    if isinstance(value, Unset):
        return None
    protocols = _opt(value.protocols)
    return PubproxyDetail(
        entry=_opt(value.entry),
        exit=_opt(value.exit_),
        protocols=None if protocols is None else tuple(protocols),
        num_ports=_opt(value.num_ports),
        num_proxies=_opt(value.num_proxies),
        last_seen=_opt(value.last_seen),
        last_usable=_opt(value.last_usable),
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
    client_id_metadata_document_supported: bool | None = None
    service_documentation: str | None = None
    registration_endpoint: str | None = None


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
class Pkce:
    """One sign-in's PKCE pair: `challenge` goes in the authorization URL, `verifier` to the
    code exchange. The verifier is left out of the repr, so logging the pair does not leak it.
    """

    verifier: str = field(repr=False)
    challenge: str
    method: Literal["S256"] = "S256"


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


@dataclass(frozen=True, slots=True)
class ClientRegistration:
    """A registered client, public and with no secret: it proves each sign-in with PKCE.

    `client_id` goes to `authorization_url` and `exchange_authorization_code`.
    `client_id_issued_at` is Unix seconds, and `client_name` the name the person will see,
    a placeholder when none was given or none can be shown. `token_endpoint_auth_method` is
    always `none`, and `scope` the most this client may be granted.
    """

    client_id: str
    client_id_issued_at: int
    client_name: str
    redirect_uris: tuple[str, ...]
    token_endpoint_auth_method: str
    grant_types: tuple[str, ...] | None = None
    response_types: tuple[str, ...] | None = None
    scope: str | None = None


def to_oauth_metadata(body: Any, status: int) -> OauthMetadata:
    return OauthMetadata(**_members(body, _OAUTH_METADATA, status))


def to_device_authorization(body: Any, status: int) -> DeviceAuthorization:
    return DeviceAuthorization(**_members(body, _DEVICE_AUTHORIZATION, status))


def to_token_response(body: Any, status: int) -> TokenResponse:
    return TokenResponse(**_members(body, _TOKEN_RESPONSE, status))


def to_client_registration(body: Any, status: int) -> ClientRegistration:
    return ClientRegistration(**_members(body, _CLIENT_REGISTRATION, status))


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
    "client_id_metadata_document_supported": ("bool", False),
    "service_documentation": ("str", False),
    "registration_endpoint": ("str", False),
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

_CLIENT_REGISTRATION: dict[str, _Member] = {
    "client_id": ("str", True),
    "client_id_issued_at": ("int", True),
    "client_name": ("str", True),
    "redirect_uris": ("strs", True),
    "token_endpoint_auth_method": ("str", True),
    "grant_types": ("strs", False),
    "response_types": ("strs", False),
    "scope": ("str", False),
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

"""What the API answers, and the one place the wire shape becomes an idiomatic one."""

from __future__ import annotations

import dataclasses
import datetime
import enum
import re
import sys
import types
import typing
from dataclasses import dataclass, field
from typing import Any, Literal, TypeVar, get_args

from ._generated import models as _generated_models
from ._generated.models.database_format import DatabaseFormat
from ._generated.models.database_license_type_type_1 import DatabaseLicenseTypeType1
from ._generated.models.lookup_response import LookupResponse
from ._generated.models.standing import Standing
from ._generated.types import Unset
from .errors import VPNDetectionError

__all__ = [
    "DATABASE_FORMATS",
    "LICENSE_TYPES",
    "STANDINGS",
    "AbuseContact",
    "BitTorrentDetail",
    "CarrierDetail",
    "ClassDetail",
    "Company",
    "DeviceAuthorization",
    "DnsResolverDetail",
    "Flag",
    "Format",
    "OauthMetadata",
    "ProxyDetail",
    "PubproxyDetail",
    "Result",
    "SatelliteDetail",
    "SmtpDetail",
    "SshDetail",
    "TokenResponse",
    "VpnDetail",
    "WebDetail",
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
    "is_anycast",
    "is_carrier",
    "is_satellite",
    "is_ssh",
    "is_smtp",
    "is_web",
    "is_dns_resolver",
    "is_bittorrent",
]

Format = Literal["csvgz", "mmdb"]

DATABASE_FORMATS: tuple[Format, ...] = get_args(Format)
"""Every `Format`, at runtime.

A `Literal` is erased to nothing a program can check against, so a format read from a flag,
a form or a config file has these to be tested against before a call.
"""


def wire_format(format: object) -> DatabaseFormat:
    """`format` as a request names it. An answer may carry a format this release was not
    built with, which reads as served, but a request naming one is refused here, before the
    network, as the API would refuse it a round trip later."""
    if not isinstance(format, str) or format not in DATABASE_FORMATS:
        raise ValueError(f"{format!r} is not a valid DatabaseFormat")
    return DatabaseFormat(format)


STANDINGS: tuple[str, ...] = tuple(member.value for member in Standing)
"""Every `standing` a database family can carry, at runtime, read off the pinned spec."""

LICENSE_TYPES: tuple[str, ...] = tuple(member.value for member in DatabaseLicenseTypeType1)
"""Every `license_type`, at runtime, read off the pinned spec. `None`, for no license, is not
one of them."""


@dataclass(frozen=True, slots=True)
class VpnDetail:
    """What is known about the VPN attribution.

    Every field is populated when the object itself is, empty values included.
    `provider` is the ID to key on, and `provider_name` the name the provider catalog
    gives it, as every detail with a provider carries. `method` is deprecated: no plan is answered with it since 2026-10-20, so it is
    `None`; read `confidence` instead. It stays until the next major.
    """

    provider: str | None = None
    last_seen: datetime.date | None = None
    confidence: str | None = None
    method: str | None = None
    provider_name: str | None = None


@dataclass(frozen=True, slots=True)
class ClassDetail:
    """The shared detail shape for the hosting, relay, tor and cdn datasets."""

    provider: str | None = None
    confidence: str | None = None
    last_seen: datetime.date | None = None
    provider_name: str | None = None


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
    provider_name: str | None = None


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
class CarrierDetail:
    """The mobile carrier, from Carrier IP. Empty (every field `None`) when `is_carrier`
    is false."""

    name: str | None = None
    mcc: str | None = None
    mnc: str | None = None
    country: str | None = None
    confidence: str | None = None


@dataclass(frozen=True, slots=True)
class SatelliteDetail:
    """The satellite operator, from Satellite IP. Empty when `is_satellite` is false."""

    provider: str | None = None
    provider_name: str | None = None
    orbit: str | None = None
    segment: str | None = None
    country: str | None = None
    asn: int | None = None
    confidence: str | None = None


@dataclass(frozen=True, slots=True)
class SshDetail:
    """The SSH server answering here. Empty when `is_ssh` is false."""

    port: int | None = None
    banner: str | None = None
    host_key_fp: str | None = None
    session_ok: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None


@dataclass(frozen=True, slots=True)
class SmtpDetail:
    """The SMTP server answering here. Empty when `is_smtp` is false."""

    port: int | None = None
    banner: str | None = None
    session_ok: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None


@dataclass(frozen=True, slots=True)
class WebDetail:
    """One port of Web IP that answered. `Result.web` is a tuple of these, empty when
    `is_web` is false."""

    port: int
    tls_ok: bool
    session_ok: bool
    status_code: int
    server: str
    location: str
    title: str
    cert_subject_cn: str
    cert_subject_o: str
    cert_issuer_dn: str
    cert_browser_trusted: bool
    tls_version: str
    first_seen: str
    last_seen: str


@dataclass(frozen=True, slots=True)
class DnsResolverDetail:
    """The open DNS resolver answering here. Empty when `is_dns_resolver` is false."""

    port: int | None = None
    recursion_available: bool | None = None
    rcode: int | None = None
    answer_correct: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None


@dataclass(frozen=True, slots=True)
class BitTorrentDetail:
    """BitTorrent clients seen here. Empty when `is_bittorrent` is false."""

    verified: bool | None = None
    id_matches_ip: bool | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    last_reachable: str | None = None
    days_seen: int | None = None
    num_ports: int | None = None
    peak_num_ports: int | None = None
    indexer: bool | None = None
    clients: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class Location:
    """Where the address is, on every answer, with or without a key.

    Every field is set whenever the object is, an empty string where it is not known. The
    region, city, postal code, coordinates and the rest from `region` on are on a paid
    plan's answers, and `None` where your plan does not include them.
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
    region: str | None = None
    region_code: str | None = None
    city: str | None = None
    postal_code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    accuracy_radius: int | None = None
    geoname_id: str | None = None
    dma_code: str | None = None
    last_changed: str | None = None


@dataclass(frozen=True, slots=True)
class Asn:
    """The AS announcing the address, on every answer, with or without a key: `asn` is 0
    where none does. Every answer carries `country` and `rpki_status`, and one without
    them is refused as the server's failure; they are `None` only on an `Asn` built by
    hand."""

    asn: int = 0
    name: str = ""
    domain: str = ""
    type: str = ""
    prefix: str = ""
    country: str | None = None
    rpki_status: str | None = None


@dataclass(frozen=True, slots=True)
class Company:
    """Who uses the address, from IP Company, on a paid plan's answers."""

    name: str = ""
    domain: str = ""
    type: str | None = None
    country: str | None = None


@dataclass(frozen=True, slots=True)
class AbuseContact:
    """Where to report abuse from the address, from IP Abuse Contact, on a paid plan's
    answers."""

    email: str = ""
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    country: str | None = None
    network: str | None = None
    validated: bool | None = None
    unvalidated_since: str | None = None


@dataclass(frozen=True, slots=True)
class Result:
    """What a lookup answers.

    An **optional** member is one your plan does not include. It never means "we could
    not check", so `None` and `False` are genuinely different answers: `None` is "not in
    your plan", `False` is "checked, and no". Use `flagged()` when you only care whether
    the address is flagged.

    A detail object that is present but empty (every field `None`, `web` an empty tuple)
    means the flag above it is false. A populated one always carries every one of its keys.

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

    #: On answers to a key on the free plan only: False while its organization's trial of
    #: every field lasts, True once the answer has Unlimited's.
    trial_expired: bool | None = None

    #: On answers to a key on a paid plan only: False while the answer has every field, True
    #: once its organization's overage cap is reached and the answer has Unlimited's. Lookups
    #: answered past the cap are not billed.
    cap_reached: bool | None = None

    # The members below came after the ones above, and go last so a `Result` built by hand
    # positionally still builds. `is_anycast` and `hostname` are on every plan's answers,
    # the rest on a paid plan's.
    is_anycast: bool | None = None
    is_carrier: bool | None = None
    is_satellite: bool | None = None
    is_ssh: bool | None = None
    is_smtp: bool | None = None
    is_web: bool | None = None
    is_dns_resolver: bool | None = None
    is_bittorrent: bool | None = None

    carrier: CarrierDetail | None = None
    satellite: SatelliteDetail | None = None
    ssh: SshDetail | None = None
    smtp: SmtpDetail | None = None
    #: Every port of Web IP that answered, an empty tuple when `is_web` is false.
    web: tuple[WebDetail, ...] | None = None
    dns_resolver: DnsResolverDetail | None = None
    bittorrent: BitTorrentDetail | None = None

    company: Company | None = None
    #: The address's reverse DNS name, the empty string where it has none.
    hostname: str | None = None
    abuse: AbuseContact | None = None

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
    parsed = LookupResponse.from_dict(rfc3339(LookupResponse, body))
    check_answer(parsed)
    # The generated model takes any value it finds, so `"ip": null` or `"is_vpn": "yes"`
    # came back as the answer, from a lookup and a batch entry alike (5.7.1, measured
    # 2026-10-15). Each is the server's failure, raised for the caller to report as one.
    if not isinstance(parsed.ip, str) or parsed.ip == "":
        raise TypeError(f"the answer's ip is not an address: {parsed.ip!r}")
    for flag in (*_FLAGS, "is_bogon", "trial_expired", "cap_reached"):
        value = getattr(parsed, flag)
        if not isinstance(value, bool) and not (
            flag != "is_vpn" and isinstance(value, Unset | None)
        ):
            raise TypeError(f"the answer's {flag} is not a boolean: {value!r}")
    return Result(
        ip=parsed.ip,
        is_vpn=parsed.is_vpn,
        is_bogon=parsed.is_bogon is True,
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
        trial_expired=_opt(parsed.trial_expired),
        cap_reached=_opt(parsed.cap_reached),
        is_anycast=_opt(parsed.is_anycast),
        is_carrier=_opt(parsed.is_carrier),
        is_satellite=_opt(parsed.is_satellite),
        is_ssh=_opt(parsed.is_ssh),
        is_smtp=_opt(parsed.is_smtp),
        is_web=_opt(parsed.is_web),
        is_dns_resolver=_opt(parsed.is_dns_resolver),
        is_bittorrent=_opt(parsed.is_bittorrent),
        carrier=_detail(CarrierDetail, parsed.carrier),
        satellite=_detail(SatelliteDetail, parsed.satellite),
        ssh=_detail(SshDetail, parsed.ssh),
        smtp=_detail(SmtpDetail, parsed.smtp),
        web=_web(parsed.web),
        dns_resolver=_detail(DnsResolverDetail, parsed.dns_resolver),
        bittorrent=_bittorrent(parsed.bittorrent),
        company=_company(parsed.company),
        hostname=_opt(parsed.hostname),
        abuse=_detail(AbuseContact, parsed.abuse),
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


# The spec's `date-time` and `date` are RFC 3339's, and only those are read. The generated
# models parse with `fromisoformat`, which took a date-time with no offset as a naive
# datetime, which no aware one can be compared with, a date alone as midnight, `+0500`, `+05`,
# `+05:60` as an hour more, a space for the `T`, no seconds, a comma for the point, week dates
# and `20261005` (5.12.0, measured 2026-10-25). RFC 3339 also allows a lowercase `t` and `z`:
# this check refused both and `fromisoformat` refuses the `z` (Python 3.11 and 3.12), so 5.12.2
# refused `2026-10-05t10:00:00z` as an answer it could not read (measured 2026-10-28). Both are
# read now, and a date-time reaches the generated decoder in capitals.
_FULL_DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")
_DATE_TIME = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.[0-9]+)?"
    r"(?:[Zz]|[+-]([0-9]{2}):([0-9]{2}))"
)


def rfc3339(model: type, body: Any) -> Any:
    """`body`, once every date its model names, at any depth, is in RFC 3339's form, on a
    day, hour, second and offset that exist, each date-time's `t` and `z` in capitals for
    the generated decoder. Raises ValueError otherwise. `body` itself is never changed,
    since a lookup hands it on as `raw`."""
    fields = getattr(model, "__attrs_attrs__", None)
    if fields is None or not isinstance(body, dict):
        return body
    hints = _hints(model)
    read = body
    for member_field in fields:
        name = member_field.name
        if name in body:
            value = _check_date(hints.get(name, Any), body[name], name)
            if value is not body[name]:
                read = {**read, name: value}
    return read


def _check_date(hint: Any, value: Any, name: str) -> Any:
    arms = _arms(hint)
    if isinstance(value, str):
        if datetime.datetime in arms:
            return _date_time(value, name)
        if datetime.date in arms:
            _date(value, name)
    elif isinstance(value, dict):
        for arm in arms:
            if hasattr(arm, "__attrs_attrs__"):
                value = rfc3339(arm, value)
    elif isinstance(value, list):
        for arm in arms:
            if typing.get_origin(arm) is list and typing.get_args(arm):
                items = [_check_date(typing.get_args(arm)[0], item, name) for item in value]
                if any(read is not item for read, item in zip(items, value, strict=True)):
                    value = items
    return value


def _arms(hint: Any) -> tuple[Any, ...]:
    origin = typing.get_origin(hint)
    if origin is typing.Union or origin is types.UnionType:
        return tuple(arm for part in typing.get_args(hint) for arm in _arms(part))
    return (hint,)


def _date(value: str, name: str) -> None:
    match = _FULL_DATE.fullmatch(value)
    if match is None:
        raise ValueError(f"{name} is not an RFC 3339 date: {value!r}")
    # A day its month lacks, 30 February, raises here.
    datetime.date(int(match[1]), int(match[2]), int(match[3]))


def _date_time(value: str, name: str) -> str:
    match = _DATE_TIME.fullmatch(value)
    if match is None:
        raise ValueError(f"{name} is not an RFC 3339 date-time: {value!r}")
    year, month, day, hour, minute, second, offset_hour, offset_minute = match.groups()
    if offset_hour is not None and (int(offset_hour) > 23 or int(offset_minute) > 59):
        raise ValueError(f"{name} has no such offset: {value!r}")
    # 30 February, an hour of 24 and a leap second raise here.
    datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    # Its only letters are the `T` and the `Z`.
    capitals = value.upper()
    return value if capitals == value else capitals


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
    "is_anycast",
    "is_carrier",
    "is_satellite",
    "is_ssh",
    "is_smtp",
    "is_web",
    "is_dns_resolver",
    "is_bittorrent",
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
        provider_name=_opt(value.provider_name),
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
        region=_opt(value.region),
        region_code=_opt(value.region_code),
        city=_opt(value.city),
        postal_code=_opt(value.postal_code),
        latitude=None if isinstance(value.latitude, Unset) else float(value.latitude),
        longitude=None if isinstance(value.longitude, Unset) else float(value.longitude),
        accuracy_radius=_opt(value.accuracy_radius),
        geoname_id=_opt(value.geoname_id),
        dma_code=_opt(value.dma_code),
        last_changed=_opt(value.last_changed),
    )


def _asn(value: Any) -> Asn | None:
    if isinstance(value, Unset):
        return None
    return Asn(
        asn=value.asn,
        name=value.name,
        domain=value.domain,
        type=value.type_,
        prefix=value.prefix,
        country=_opt(value.country),
        rpki_status=_opt(value.rpki_status),
    )


D = TypeVar("D")


def _detail(cls: type[D], value: Any) -> D | None:
    """A detail whose wire members carry the same names as its fields, each `UNSET` read
    as `None`."""
    if isinstance(value, Unset):
        return None
    fields = dataclasses.fields(cls)  # type: ignore[arg-type]
    return cls(**{f.name: _opt(getattr(value, f.name)) for f in fields})


def _web(value: Any) -> tuple[WebDetail, ...] | None:
    if isinstance(value, Unset):
        return None
    return tuple(
        WebDetail(**{f.name: getattr(row, f.name) for f in dataclasses.fields(WebDetail)})
        for row in value
    )


def _bittorrent(value: Any) -> BitTorrentDetail | None:
    if isinstance(value, Unset):
        return None
    clients = _opt(value.clients)
    return BitTorrentDetail(
        verified=_opt(value.verified),
        id_matches_ip=_opt(value.id_matches_ip),
        first_seen=_opt(value.first_seen),
        last_seen=_opt(value.last_seen),
        last_reachable=_opt(value.last_reachable),
        days_seen=_opt(value.days_seen),
        num_ports=_opt(value.num_ports),
        peak_num_ports=_opt(value.peak_num_ports),
        indexer=_opt(value.indexer),
        clients=None if clients is None else tuple(clients),
    )


def _company(value: Any) -> Company | None:
    if isinstance(value, Unset):
        return None
    return Company(
        name=value.name, domain=value.domain, type=_opt(value.type_), country=_opt(value.country)
    )


def _class(value: Any) -> ClassDetail | None:
    if isinstance(value, Unset):
        return None
    return ClassDetail(
        provider=_opt(value.provider),
        confidence=_opt(value.confidence),
        last_seen=_opt(value.last_seen),
        provider_name=_opt(value.provider_name),
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
        provider_name=_opt(value.provider_name),
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

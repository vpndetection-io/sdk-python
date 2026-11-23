"""Locally answerable addresses: the ones that can never be VPN infrastructure."""

from __future__ import annotations

import ipaddress

from ._bogons import BOGON_V4, BOGON_V6
from .models import (
    AbuseContact,
    Asn,
    BitTorrentDetail,
    BotDetail,
    CarrierDetail,
    ClassDetail,
    Company,
    DnsResolverDetail,
    Location,
    ProxyDetail,
    PubproxyDetail,
    Result,
    SatelliteDetail,
    SmtpDetail,
    SshDetail,
    UserAgent,
    VpnDetail,
)

__all__ = ["bogon_result", "is_bogon"]


def is_bogon(ip: str) -> bool:
    """Whether an address is a bogon: private, loopback, link-local, documentation,
    multicast or otherwise not routable on the public internet, including the IPv6
    equivalents and the 6to4 and Teredo ranges that wrap them.

    These can never be VPN or proxy infrastructure, so the client answers them itself
    and they never cost a request. Anything that is not a valid address is False, so
    the API gets to be the one that rejects it. An IPv4-mapped address
    (``::ffff:8.8.8.8``) is judged as the IPv4 address it carries.
    """
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if addr.version == 6 and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    value = int(addr)
    ranges = _v6_ranges() if addr.version == 6 else _v4_ranges()
    return any(value & mask == net for net, mask in ranges)


def unmapped(ip: str) -> str:
    """The IPv4 address an IPv4-mapped IPv6 address carries, dotted, and any other
    string as given. A server listening on ``::`` sees an IPv4 visitor in the mapped
    form, which read whole is inside ``::ffff:0:0/96`` and so would be answered as a
    bogon with no request made.
    """
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    if addr.version == 6 and addr.ipv4_mapped is not None:
        return str(addr.ipv4_mapped)
    return ip


def bogon_result(ip: str) -> Result:
    """The answer a bogon gets, in the full shape the API serves at its widest plan:
    every flag present and false, every detail object present and empty, `web` an empty
    tuple, `hostname` the empty string, and `location`, `asn`, `company` and `abuse` with
    every field empty or zero, as the API answers a bogon.

    `is_bogon` is True, as the API answers reserved space. Note this is deliberately the WIDEST shape regardless of your plan, so
    do not infer which fields your plan includes from a bogon answer.
    """
    return Result(
        ip=ip,
        is_bogon=True,
        is_vpn=False,
        is_hosting=False,
        is_relay=False,
        is_tor=False,
        is_cdn=False,
        is_resproxy=False,
        is_dcproxy=False,
        is_mobproxy=False,
        is_pubproxy=False,
        vpn=VpnDetail(),
        hosting=ClassDetail(),
        relay=ClassDetail(),
        tor=ClassDetail(),
        cdn=ClassDetail(),
        resproxy=ProxyDetail(),
        dcproxy=ProxyDetail(),
        mobproxy=ProxyDetail(),
        pubproxy=PubproxyDetail(),
        location=Location(
            region="",
            region_code="",
            city="",
            postal_code="",
            latitude=0.0,
            longitude=0.0,
            accuracy_radius=0,
            geoname_id="",
            dma_code="",
            last_changed="",
        ),
        asn=Asn(country="", rpki_status=""),
        raw={},
        is_anycast=False,
        is_carrier=False,
        is_satellite=False,
        is_ssh=False,
        is_smtp=False,
        is_web=False,
        is_dns_resolver=False,
        is_bittorrent=False,
        carrier=CarrierDetail(),
        satellite=SatelliteDetail(),
        ssh=SshDetail(),
        smtp=SmtpDetail(),
        web=(),
        dns_resolver=DnsResolverDetail(),
        bittorrent=BitTorrentDetail(),
        company=Company(type="", country=""),
        hostname="",
        abuse=AbuseContact(
            name="",
            phone="",
            address="",
            country="",
            network="",
            validated=False,
            unvalidated_since="",
        ),
        is_bot=False,
        bot=BotDetail(),
        user_agent=UserAgent(),
    )


# Parsed once on first use rather than at import: a consumer that never looks up an
# address should not pay for the table, and module-scope work is what makes a library
# expensive to import.
_V4_RANGES: tuple[tuple[int, int], ...] | None = None
_V6_RANGES: tuple[tuple[int, int], ...] | None = None


def _v4_ranges() -> tuple[tuple[int, int], ...]:
    global _V4_RANGES
    if _V4_RANGES is None:
        _V4_RANGES = _parse(BOGON_V4)
    return _V4_RANGES


def _v6_ranges() -> tuple[tuple[int, int], ...]:
    global _V6_RANGES
    if _V6_RANGES is None:
        _V6_RANGES = _parse(BOGON_V6)
    return _V6_RANGES


def _parse(cidrs: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    nets = [ipaddress.ip_network(c) for c in cidrs]
    return tuple((int(n.network_address), int(n.netmask)) for n in nets)

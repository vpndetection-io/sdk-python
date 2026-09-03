"""Locally answerable addresses: the ones that can never be VPN infrastructure."""

from __future__ import annotations

import ipaddress

from ._bogons import BOGON_V4, BOGON_V6
from .models import ClassDetail, ProxyDetail, Result, VpnDetail

__all__ = ["bogon_result", "is_bogon"]


def is_bogon(ip: str) -> bool:
    """Whether an address is a bogon: private, loopback, link-local, documentation,
    multicast or otherwise not routable on the public internet, including the IPv6
    equivalents and the 6to4 and Teredo ranges that wrap them.

    These can never be VPN or proxy infrastructure, so the client answers them itself
    and they never cost a request. Anything that is not a valid address is False, so
    the API gets to be the one that rejects it.
    """
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    value = int(addr)
    ranges = _v6_ranges() if addr.version == 6 else _v4_ranges()
    return any(value & mask == net for net, mask in ranges)


def bogon_result(ip: str) -> Result:
    """The answer a bogon gets, in the full shape the API serves at its widest plan:
    every flag present and false, every detail object present and empty.

    `is_bogon` is set so a caller can always tell a locally computed answer from a
    served one. Note this is deliberately the WIDEST shape regardless of your plan, so
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
        vpn=VpnDetail(),
        hosting=ClassDetail(),
        relay=ClassDetail(),
        tor=ClassDetail(),
        cdn=ClassDetail(),
        resproxy=ProxyDetail(),
        dcproxy=ProxyDetail(),
        mobproxy=ProxyDetail(),
        raw={},
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

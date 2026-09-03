from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.class_detail import ClassDetail
    from ..models.proxy_detail import ProxyDetail
    from ..models.vpn_detail import VpnDetail


T = TypeVar("T", bound="LookupResponse")


@_attrs_define
class LookupResponse:
    """The union of every plan's answer. Only `ip` and `is_vpn` are guaranteed;
    each remaining field is present when your plan includes it, and absent
    otherwise. A client that must work across plans should treat an absent
    flag as unknown rather than as `false`.

        Attributes:
            ip (str): The address that was looked up, normalized. Example: 1.1.1.1.
            is_vpn (bool): Whether the address is VPN infrastructure. Keys off presence in the
                VPN dataset, so an unattributed range with no provider is still
                `true`.
            is_hosting (bool | Unset): Whether the address belongs to a hosting or cloud provider. Starter and above.
            is_relay (bool | Unset): Whether the address is a privacy relay egress. Starter and above.
            is_tor (bool | Unset): Whether the address is a Tor node. Starter and above.
            is_cdn (bool | Unset): Whether the address belongs to a CDN. Starter and above.
            is_resproxy (bool | Unset): Whether the address was seen in a residential proxy pool. Max only.
            is_dcproxy (bool | Unset): Whether the address was seen in a datacenter proxy pool. Max only.
            is_mobproxy (bool | Unset): Whether the address was seen in a mobile proxy pool. Max only.
            vpn (VpnDetail | Unset): What is known about the VPN attribution. Every key is present when the
                object is populated, empty values included; the object is `{}` when
                `is_vpn` is false. `confidence` and `method` are max only, so on a lower
                plan they are absent from a populated object rather than empty.
            hosting (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            relay (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            tor (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            cdn (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            resproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. Every key is present
                when the object is populated; the object is `{}` when its flag is false.
            dcproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. Every key is present
                when the object is populated; the object is `{}` when its flag is false.
            mobproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. Every key is present
                when the object is populated; the object is `{}` when its flag is false.
    """

    ip: str
    is_vpn: bool
    is_hosting: bool | Unset = UNSET
    is_relay: bool | Unset = UNSET
    is_tor: bool | Unset = UNSET
    is_cdn: bool | Unset = UNSET
    is_resproxy: bool | Unset = UNSET
    is_dcproxy: bool | Unset = UNSET
    is_mobproxy: bool | Unset = UNSET
    vpn: VpnDetail | Unset = UNSET
    hosting: ClassDetail | Unset = UNSET
    relay: ClassDetail | Unset = UNSET
    tor: ClassDetail | Unset = UNSET
    cdn: ClassDetail | Unset = UNSET
    resproxy: ProxyDetail | Unset = UNSET
    dcproxy: ProxyDetail | Unset = UNSET
    mobproxy: ProxyDetail | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ip = self.ip

        is_vpn = self.is_vpn

        is_hosting = self.is_hosting

        is_relay = self.is_relay

        is_tor = self.is_tor

        is_cdn = self.is_cdn

        is_resproxy = self.is_resproxy

        is_dcproxy = self.is_dcproxy

        is_mobproxy = self.is_mobproxy

        vpn: dict[str, Any] | Unset = UNSET
        if not isinstance(self.vpn, Unset):
            vpn = self.vpn.to_dict()

        hosting: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hosting, Unset):
            hosting = self.hosting.to_dict()

        relay: dict[str, Any] | Unset = UNSET
        if not isinstance(self.relay, Unset):
            relay = self.relay.to_dict()

        tor: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tor, Unset):
            tor = self.tor.to_dict()

        cdn: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cdn, Unset):
            cdn = self.cdn.to_dict()

        resproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.resproxy, Unset):
            resproxy = self.resproxy.to_dict()

        dcproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dcproxy, Unset):
            dcproxy = self.dcproxy.to_dict()

        mobproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mobproxy, Unset):
            mobproxy = self.mobproxy.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ip": ip,
                "is_vpn": is_vpn,
            }
        )
        if is_hosting is not UNSET:
            field_dict["is_hosting"] = is_hosting
        if is_relay is not UNSET:
            field_dict["is_relay"] = is_relay
        if is_tor is not UNSET:
            field_dict["is_tor"] = is_tor
        if is_cdn is not UNSET:
            field_dict["is_cdn"] = is_cdn
        if is_resproxy is not UNSET:
            field_dict["is_resproxy"] = is_resproxy
        if is_dcproxy is not UNSET:
            field_dict["is_dcproxy"] = is_dcproxy
        if is_mobproxy is not UNSET:
            field_dict["is_mobproxy"] = is_mobproxy
        if vpn is not UNSET:
            field_dict["vpn"] = vpn
        if hosting is not UNSET:
            field_dict["hosting"] = hosting
        if relay is not UNSET:
            field_dict["relay"] = relay
        if tor is not UNSET:
            field_dict["tor"] = tor
        if cdn is not UNSET:
            field_dict["cdn"] = cdn
        if resproxy is not UNSET:
            field_dict["resproxy"] = resproxy
        if dcproxy is not UNSET:
            field_dict["dcproxy"] = dcproxy
        if mobproxy is not UNSET:
            field_dict["mobproxy"] = mobproxy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.class_detail import ClassDetail
        from ..models.proxy_detail import ProxyDetail
        from ..models.vpn_detail import VpnDetail

        d = dict(src_dict)
        ip = d.pop("ip")

        is_vpn = d.pop("is_vpn")

        is_hosting = d.pop("is_hosting", UNSET)

        is_relay = d.pop("is_relay", UNSET)

        is_tor = d.pop("is_tor", UNSET)

        is_cdn = d.pop("is_cdn", UNSET)

        is_resproxy = d.pop("is_resproxy", UNSET)

        is_dcproxy = d.pop("is_dcproxy", UNSET)

        is_mobproxy = d.pop("is_mobproxy", UNSET)

        _vpn = d.pop("vpn", UNSET)
        vpn: VpnDetail | Unset
        if isinstance(_vpn, Unset):
            vpn = UNSET
        else:
            vpn = VpnDetail.from_dict(_vpn)

        _hosting = d.pop("hosting", UNSET)
        hosting: ClassDetail | Unset
        if isinstance(_hosting, Unset):
            hosting = UNSET
        else:
            hosting = ClassDetail.from_dict(_hosting)

        _relay = d.pop("relay", UNSET)
        relay: ClassDetail | Unset
        if isinstance(_relay, Unset):
            relay = UNSET
        else:
            relay = ClassDetail.from_dict(_relay)

        _tor = d.pop("tor", UNSET)
        tor: ClassDetail | Unset
        if isinstance(_tor, Unset):
            tor = UNSET
        else:
            tor = ClassDetail.from_dict(_tor)

        _cdn = d.pop("cdn", UNSET)
        cdn: ClassDetail | Unset
        if isinstance(_cdn, Unset):
            cdn = UNSET
        else:
            cdn = ClassDetail.from_dict(_cdn)

        _resproxy = d.pop("resproxy", UNSET)
        resproxy: ProxyDetail | Unset
        if isinstance(_resproxy, Unset):
            resproxy = UNSET
        else:
            resproxy = ProxyDetail.from_dict(_resproxy)

        _dcproxy = d.pop("dcproxy", UNSET)
        dcproxy: ProxyDetail | Unset
        if isinstance(_dcproxy, Unset):
            dcproxy = UNSET
        else:
            dcproxy = ProxyDetail.from_dict(_dcproxy)

        _mobproxy = d.pop("mobproxy", UNSET)
        mobproxy: ProxyDetail | Unset
        if isinstance(_mobproxy, Unset):
            mobproxy = UNSET
        else:
            mobproxy = ProxyDetail.from_dict(_mobproxy)

        lookup_response = cls(
            ip=ip,
            is_vpn=is_vpn,
            is_hosting=is_hosting,
            is_relay=is_relay,
            is_tor=is_tor,
            is_cdn=is_cdn,
            is_resproxy=is_resproxy,
            is_dcproxy=is_dcproxy,
            is_mobproxy=is_mobproxy,
            vpn=vpn,
            hosting=hosting,
            relay=relay,
            tor=tor,
            cdn=cdn,
            resproxy=resproxy,
            dcproxy=dcproxy,
            mobproxy=mobproxy,
        )

        lookup_response.additional_properties = d
        return lookup_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

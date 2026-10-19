from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PubproxyDetail")


@_attrs_define
class PubproxyDetail:
    """The address in Public Proxy IP, open proxies anyone can connect
    through, measured over a rolling 90 day window. An address is either
    end of a proxy, or both: where it listens, and where its traffic
    leaves from. Every key is present when the object is populated; the
    object is `{}` when `is_pubproxy` is false.

        Attributes:
            entry (bool | Unset): Whether a public proxy listens on this address. Example: True.
            exit_ (bool | Unset): Whether a public proxy's traffic leaves from this address. Example: False.
            protocols (list[str] | Unset): The protocols of the proxies listening on or leaving from this
                address: `http`, `https` (an HTTP proxy that also tunnels HTTPS),
                `socks4` or `socks5`. Empty where only the address is known.
                 Example: ['http', 'https'].
            num_ports (int | Unset): How many distinct ports a public proxy listens on at this address;
                0 when it is only an exit, or its port is not known.
                 Example: 1.
            num_proxies (int | Unset): How many distinct public proxies' traffic left from this address;
                0 when it is only an entry.
                 Example: 0.
            last_seen (datetime.date | Unset): The most recent date within the window a proxy on this address was seen.
                Example: 2026-10-17.
            last_usable (str | Unset): The most recent date within the window a request through a proxy on
                this address was answered, as YYYY-MM-DD, or an empty string when
                none was.
                 Example: 2026-10-17.
    """

    entry: bool | Unset = UNSET
    exit_: bool | Unset = UNSET
    protocols: list[str] | Unset = UNSET
    num_ports: int | Unset = UNSET
    num_proxies: int | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    last_usable: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entry = self.entry

        exit_ = self.exit_

        protocols: list[str] | Unset = UNSET
        if not isinstance(self.protocols, Unset):
            protocols = self.protocols

        num_ports = self.num_ports

        num_proxies = self.num_proxies

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        last_usable = self.last_usable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry is not UNSET:
            field_dict["entry"] = entry
        if exit_ is not UNSET:
            field_dict["exit"] = exit_
        if protocols is not UNSET:
            field_dict["protocols"] = protocols
        if num_ports is not UNSET:
            field_dict["num_ports"] = num_ports
        if num_proxies is not UNSET:
            field_dict["num_proxies"] = num_proxies
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if last_usable is not UNSET:
            field_dict["last_usable"] = last_usable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        entry = d.pop("entry", UNSET)

        exit_ = d.pop("exit", UNSET)

        protocols = cast(list[str], d.pop("protocols", UNSET))

        num_ports = d.pop("num_ports", UNSET)

        num_proxies = d.pop("num_proxies", UNSET)

        _last_seen = d.pop("last_seen", UNSET)
        last_seen: datetime.date | Unset
        if isinstance(_last_seen, Unset):
            last_seen = UNSET
        else:
            last_seen = datetime.date.fromisoformat(_last_seen)

        last_usable = d.pop("last_usable", UNSET)

        pubproxy_detail = cls(
            entry=entry,
            exit_=exit_,
            protocols=protocols,
            num_ports=num_ports,
            num_proxies=num_proxies,
            last_seen=last_seen,
            last_usable=last_usable,
        )

        pubproxy_detail.additional_properties = d
        return pubproxy_detail

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

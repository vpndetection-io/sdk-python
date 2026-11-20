from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BitTorrentDetail")


@_attrs_define
class BitTorrentDetail:
    """BitTorrent clients seen on the address over the last 90 days, from our
    BitTorrent IP database. Every key is present when the object is
    populated; the object is `{}` when `is_bittorrent` is false.

        Attributes:
            verified (bool | Unset): A client here answered, or two or more reported it at once. Example: True.
            id_matches_ip (bool | Unset): A client here derived its node ID from the address (BEP 42). Example: False.
            first_seen (str | Unset): The first day a client was seen here. Example: 2026-08-21.
            last_seen (str | Unset): The last day. Example: 2026-11-15.
            last_reachable (str | Unset): The last day one answered, empty when none did. Example: 2026-11-14.
            days_seen (int | Unset): On how many days. Example: 37.
            num_ports (int | Unset): Distinct ports over the window. Example: 4.
            peak_num_ports (int | Unset): The most on one day. Example: 2.
            indexer (bool | Unset): A DHT indexer rather than people. Example: False.
            clients (list[str] | Unset): The two-letter codes its clients name themselves by. Example: ['qB', 'TR'].
    """

    verified: bool | Unset = UNSET
    id_matches_ip: bool | Unset = UNSET
    first_seen: str | Unset = UNSET
    last_seen: str | Unset = UNSET
    last_reachable: str | Unset = UNSET
    days_seen: int | Unset = UNSET
    num_ports: int | Unset = UNSET
    peak_num_ports: int | Unset = UNSET
    indexer: bool | Unset = UNSET
    clients: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        verified = self.verified

        id_matches_ip = self.id_matches_ip

        first_seen = self.first_seen

        last_seen = self.last_seen

        last_reachable = self.last_reachable

        days_seen = self.days_seen

        num_ports = self.num_ports

        peak_num_ports = self.peak_num_ports

        indexer = self.indexer

        clients: list[str] | Unset = UNSET
        if not isinstance(self.clients, Unset):
            clients = self.clients

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if verified is not UNSET:
            field_dict["verified"] = verified
        if id_matches_ip is not UNSET:
            field_dict["id_matches_ip"] = id_matches_ip
        if first_seen is not UNSET:
            field_dict["first_seen"] = first_seen
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if last_reachable is not UNSET:
            field_dict["last_reachable"] = last_reachable
        if days_seen is not UNSET:
            field_dict["days_seen"] = days_seen
        if num_ports is not UNSET:
            field_dict["num_ports"] = num_ports
        if peak_num_ports is not UNSET:
            field_dict["peak_num_ports"] = peak_num_ports
        if indexer is not UNSET:
            field_dict["indexer"] = indexer
        if clients is not UNSET:
            field_dict["clients"] = clients

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        verified = d.pop("verified", UNSET)

        id_matches_ip = d.pop("id_matches_ip", UNSET)

        first_seen = d.pop("first_seen", UNSET)

        last_seen = d.pop("last_seen", UNSET)

        last_reachable = d.pop("last_reachable", UNSET)

        days_seen = d.pop("days_seen", UNSET)

        num_ports = d.pop("num_ports", UNSET)

        peak_num_ports = d.pop("peak_num_ports", UNSET)

        indexer = d.pop("indexer", UNSET)

        clients = cast(list[str], d.pop("clients", UNSET))

        bit_torrent_detail = cls(
            verified=verified,
            id_matches_ip=id_matches_ip,
            first_seen=first_seen,
            last_seen=last_seen,
            last_reachable=last_reachable,
            days_seen=days_seen,
            num_ports=num_ports,
            peak_num_ports=peak_num_ports,
            indexer=indexer,
            clients=clients,
        )

        bit_torrent_detail.additional_properties = d
        return bit_torrent_detail

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

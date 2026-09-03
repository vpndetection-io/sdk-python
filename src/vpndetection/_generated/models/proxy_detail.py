from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProxyDetail")


@_attrs_define
class ProxyDetail:
    """The shared detail shape for the residential, datacenter and mobile proxy
    families, measured over a rolling 90 day window. Every key is present
    when the object is populated; the object is `{}` when its flag is false.

        Attributes:
            provider (str | Unset): The proxy network, or an empty string where unattributed. Example: brightdata.
            first_seen (datetime.date | Unset): The earliest date within the window this address was seen in the pool.
                Example: 2026-06-14.
            last_seen (datetime.date | Unset): The most recent date within the window this address was seen in the pool.
                Example: 2026-09-02.
            hits (int | Unset): How many times the address was observed in the pool during the window. Example: 42.
            hits_days_pct (int | Unset): The share of days in the window on which the address was seen, as a
                percentage. A high value means a stable pool member rather than a
                one-off sighting.
                 Example: 63.
            providers_num (int | Unset): How many distinct proxy networks this address was seen in. Example: 2.
    """

    provider: str | Unset = UNSET
    first_seen: datetime.date | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    hits: int | Unset = UNSET
    hits_days_pct: int | Unset = UNSET
    providers_num: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        first_seen: str | Unset = UNSET
        if not isinstance(self.first_seen, Unset):
            first_seen = self.first_seen.isoformat()

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        hits = self.hits

        hits_days_pct = self.hits_days_pct

        providers_num = self.providers_num

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if first_seen is not UNSET:
            field_dict["first_seen"] = first_seen
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if hits is not UNSET:
            field_dict["hits"] = hits
        if hits_days_pct is not UNSET:
            field_dict["hits_days_pct"] = hits_days_pct
        if providers_num is not UNSET:
            field_dict["providers_num"] = providers_num

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        provider = d.pop("provider", UNSET)

        _first_seen = d.pop("first_seen", UNSET)
        first_seen: datetime.date | Unset
        if isinstance(_first_seen, Unset):
            first_seen = UNSET
        else:
            first_seen = datetime.date.fromisoformat(_first_seen)

        _last_seen = d.pop("last_seen", UNSET)
        last_seen: datetime.date | Unset
        if isinstance(_last_seen, Unset):
            last_seen = UNSET
        else:
            last_seen = datetime.date.fromisoformat(_last_seen)

        hits = d.pop("hits", UNSET)

        hits_days_pct = d.pop("hits_days_pct", UNSET)

        providers_num = d.pop("providers_num", UNSET)

        proxy_detail = cls(
            provider=provider,
            first_seen=first_seen,
            last_seen=last_seen,
            hits=hits,
            hits_days_pct=hits_days_pct,
            providers_num=providers_num,
        )

        proxy_detail.additional_properties = d
        return proxy_detail

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

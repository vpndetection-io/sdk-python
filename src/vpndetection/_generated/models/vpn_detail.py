from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VpnDetail")


@_attrs_define
class VpnDetail:
    """What is known about the VPN attribution. Every key is present when the
    object is populated, empty values included; the object is `{}` when
    `is_vpn` is false. `confidence` and `method` are max only, so on a lower
    plan they are absent from a populated object rather than empty.

        Attributes:
            provider (str | Unset): The VPN provider, or an empty string for an unattributed range. Example: mullvad.
            last_seen (datetime.date | Unset): The most recent date this address was observed as VPN infrastructure.
                Example: 2026-09-02.
            confidence (str | Unset): How strongly the attribution is supported. Max only. Example: high.
            method (str | Unset): How the address was attributed to the provider. Max only. Example: openvpn_cert.
    """

    provider: str | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    confidence: str | Unset = UNSET
    method: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        confidence = self.confidence

        method = self.method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if method is not UNSET:
            field_dict["method"] = method

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        provider = d.pop("provider", UNSET)

        _last_seen = d.pop("last_seen", UNSET)
        last_seen: datetime.date | Unset
        if isinstance(_last_seen, Unset):
            last_seen = UNSET
        else:
            last_seen = datetime.date.fromisoformat(_last_seen)

        confidence = d.pop("confidence", UNSET)

        method = d.pop("method", UNSET)

        vpn_detail = cls(
            provider=provider,
            last_seen=last_seen,
            confidence=confidence,
            method=method,
        )

        vpn_detail.additional_properties = d
        return vpn_detail

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

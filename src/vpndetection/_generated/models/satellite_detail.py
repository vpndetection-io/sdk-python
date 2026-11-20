from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SatelliteDetail")


@_attrs_define
class SatelliteDetail:
    """The satellite operator whose space the address is, from our Satellite IP
    database. Every key is present when the object is populated; the object
    is `{}` when `is_satellite` is false.

        Attributes:
            provider (str | Unset): The operator's ID in Satellite IP Provider. Example: starlink.
            provider_name (str | Unset): The operator's name. Example: Starlink.
            orbit (str | Unset): The orbit: `leo`, `meo` or `geo`. Example: leo.
            segment (str | Unset): Who the space serves, such as consumer or maritime. Example: consumer.
            country (str | Unset): ISO 3166 country code. Example: US.
            asn (int | Unset): The AS the operator announces it from. Example: 14593.
            confidence (str | Unset): `high`, `medium` or `low`. Example: high.
    """

    provider: str | Unset = UNSET
    provider_name: str | Unset = UNSET
    orbit: str | Unset = UNSET
    segment: str | Unset = UNSET
    country: str | Unset = UNSET
    asn: int | Unset = UNSET
    confidence: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        provider_name = self.provider_name

        orbit = self.orbit

        segment = self.segment

        country = self.country

        asn = self.asn

        confidence = self.confidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if orbit is not UNSET:
            field_dict["orbit"] = orbit
        if segment is not UNSET:
            field_dict["segment"] = segment
        if country is not UNSET:
            field_dict["country"] = country
        if asn is not UNSET:
            field_dict["asn"] = asn
        if confidence is not UNSET:
            field_dict["confidence"] = confidence

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        provider = d.pop("provider", UNSET)

        provider_name = d.pop("provider_name", UNSET)

        orbit = d.pop("orbit", UNSET)

        segment = d.pop("segment", UNSET)

        country = d.pop("country", UNSET)

        asn = d.pop("asn", UNSET)

        confidence = d.pop("confidence", UNSET)

        satellite_detail = cls(
            provider=provider,
            provider_name=provider_name,
            orbit=orbit,
            segment=segment,
            country=country,
            asn=asn,
            confidence=confidence,
        )

        satellite_detail.additional_properties = d
        return satellite_detail

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

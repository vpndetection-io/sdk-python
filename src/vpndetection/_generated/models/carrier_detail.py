from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CarrierDetail")


@_attrs_define
class CarrierDetail:
    """The mobile network whose space the address is, from our Carrier IP
    database. Every key is present when the object is populated; the object
    is `{}` when `is_carrier` is false.

        Attributes:
            name (str | Unset): The mobile carrier. Example: T-Mobile US.
            mcc (str | Unset): Its mobile country code. Example: 310.
            mnc (str | Unset): Its mobile network code. Example: 260.
            country (str | Unset): ISO 3166 country code. Example: US.
            confidence (str | Unset): `high`, `medium` or `low`. Example: high.
    """

    name: str | Unset = UNSET
    mcc: str | Unset = UNSET
    mnc: str | Unset = UNSET
    country: str | Unset = UNSET
    confidence: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        mcc = self.mcc

        mnc = self.mnc

        country = self.country

        confidence = self.confidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if mcc is not UNSET:
            field_dict["mcc"] = mcc
        if mnc is not UNSET:
            field_dict["mnc"] = mnc
        if country is not UNSET:
            field_dict["country"] = country
        if confidence is not UNSET:
            field_dict["confidence"] = confidence

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        mcc = d.pop("mcc", UNSET)

        mnc = d.pop("mnc", UNSET)

        country = d.pop("country", UNSET)

        confidence = d.pop("confidence", UNSET)

        carrier_detail = cls(
            name=name,
            mcc=mcc,
            mnc=mnc,
            country=country,
            confidence=confidence,
        )

        carrier_detail.additional_properties = d
        return carrier_detail

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

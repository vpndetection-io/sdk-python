from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Company")


@_attrs_define
class Company:
    """Who uses the address, from our IP Company database. Paid plans. Every
    key is present whenever the object is: empty strings where no record
    covers the address.

        Attributes:
            name (str): Who uses the address. Example: M247 LTD Vienna Infrastructure.
            domain (str): Their domain. Example: m247.ro.
            type_ (str | Unset): What kind of organization: hosting, isp, business, education or government. Example:
                hosting.
            country (str | Unset): ISO 3166 country code. Example: AT.
    """

    name: str
    domain: str
    type_: str | Unset = UNSET
    country: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        domain = self.domain

        type_ = self.type_

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "domain": domain,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name")

        domain = d.pop("domain")

        type_ = d.pop("type", UNSET)

        country = d.pop("country", UNSET)

        company = cls(
            name=name,
            domain=domain,
            type_=type_,
            country=country,
        )

        company.additional_properties = d
        return company

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

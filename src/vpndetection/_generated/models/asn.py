from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Asn")


@_attrs_define
class Asn:
    """The autonomous system that announces the address. Free and paid plans.
    Each field is present whenever the object is: `asn` is 0 and the rest
    empty where no announcement covers the address.

        Attributes:
            asn (int): The AS number, 0 when no announcement covers the address. Example: 9009.
            name (str): Name of the organization that operates the AS. Example: M247 Europe SRL.
            domain (str): The AS operator's own registrable domain. Example: m247global.com.
            type_ (str): The kind of network the AS runs: isp, hosting, education, government or business. Example: hosting.
            prefix (str): The announced BGP prefix that covers the address, the most specific when several do. Example:
                146.70.116.0/24.
    """

    asn: int
    name: str
    domain: str
    type_: str
    prefix: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        asn = self.asn

        name = self.name

        domain = self.domain

        type_ = self.type_

        prefix = self.prefix

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "asn": asn,
                "name": name,
                "domain": domain,
                "type": type_,
                "prefix": prefix,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        asn = d.pop("asn")

        name = d.pop("name")

        domain = d.pop("domain")

        type_ = d.pop("type")

        prefix = d.pop("prefix")

        asn = cls(
            asn=asn,
            name=name,
            domain=domain,
            type_=type_,
            prefix=prefix,
        )

        asn.additional_properties = d
        return asn

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

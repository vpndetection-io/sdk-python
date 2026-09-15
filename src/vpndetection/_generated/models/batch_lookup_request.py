from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BatchLookupRequest")


@_attrs_define
class BatchLookupRequest:
    """
    Attributes:
        ips (list[str]): The addresses to classify, 1 to 1000 per call, counted before
            duplicates collapse. Each distinct string is one lookup.
             Example: ['1.1.1.1', '2606:4700:4700::1111'].
    """

    ips: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ips = self.ips

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ips": ips,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        ips = cast(list[str], d.pop("ips"))

        batch_lookup_request = cls(
            ips=ips,
        )

        batch_lookup_request.additional_properties = d
        return batch_lookup_request

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

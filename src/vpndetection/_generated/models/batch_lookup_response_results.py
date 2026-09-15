from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.lookup_response import LookupResponse


T = TypeVar("T", bound="BatchLookupResponseResults")


@_attrs_define
class BatchLookupResponseResults:
    """One answer per input string that was classified, keyed by the string
    as you sent it; the `ip` inside is the normalized form. Each value is
    exactly what `GET /{ip}` answers for your plan.

    """

    additional_properties: dict[str, LookupResponse] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.lookup_response import LookupResponse

        d = dict(src_dict)
        batch_lookup_response_results = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = LookupResponse.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        batch_lookup_response_results.additional_properties = additional_properties
        return batch_lookup_response_results

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> LookupResponse:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: LookupResponse) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

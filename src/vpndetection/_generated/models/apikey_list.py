from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.apikey_detail import ApikeyDetail


T = TypeVar("T", bound="ApikeyList")


@_attrs_define
class ApikeyList:
    """
    Attributes:
        rc (str):
        keys (list[ApikeyDetail]):
    """

    rc: str
    keys: list[ApikeyDetail]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rc = self.rc

        keys = []
        for keys_item_data in self.keys:
            keys_item = keys_item_data.to_dict()
            keys.append(keys_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rc": rc,
                "keys": keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.apikey_detail import ApikeyDetail

        d = dict(src_dict)
        rc = d.pop("rc")

        keys = []
        _keys = d.pop("keys")
        for keys_item_data in _keys:
            keys_item = ApikeyDetail.from_dict(keys_item_data)

            keys.append(keys_item)

        apikey_list = cls(
            rc=rc,
            keys=keys,
        )

        apikey_list.additional_properties = d
        return apikey_list

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

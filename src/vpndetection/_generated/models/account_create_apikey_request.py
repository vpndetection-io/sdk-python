from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountCreateApikeyRequest")


@_attrs_define
class AccountCreateApikeyRequest:
    """
    Attributes:
        name (str): A label you will recognise later. Shown wherever the key is listed.
        allowed_scopes (list[str] | Unset): What the new key may do. Omit for a key that carries no named scope, which
            is the safe default.
    """

    name: str
    allowed_scopes: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        allowed_scopes: list[str] | Unset = UNSET
        if not isinstance(self.allowed_scopes, Unset):
            allowed_scopes = self.allowed_scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if allowed_scopes is not UNSET:
            field_dict["allowed_scopes"] = allowed_scopes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name")

        allowed_scopes = cast(list[str], d.pop("allowed_scopes", UNSET))

        account_create_apikey_request = cls(
            name=name,
            allowed_scopes=allowed_scopes,
        )

        account_create_apikey_request.additional_properties = d
        return account_create_apikey_request

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

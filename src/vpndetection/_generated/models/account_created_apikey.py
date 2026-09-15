from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountCreatedApikey")


@_attrs_define
class AccountCreatedApikey:
    """
    Attributes:
        rc (str):
        id (UUID):
        key (str): The secret. Returned once, here, and never again.
        name (str | Unset):
        key_prefix (str | Unset):
        allowed_cidrs (list[str] | Unset):
        allowed_scopes (list[str] | Unset):
    """

    rc: str
    id: UUID
    key: str
    name: str | Unset = UNSET
    key_prefix: str | Unset = UNSET
    allowed_cidrs: list[str] | Unset = UNSET
    allowed_scopes: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rc = self.rc

        id = str(self.id)

        key = self.key

        name = self.name

        key_prefix = self.key_prefix

        allowed_cidrs: list[str] | Unset = UNSET
        if not isinstance(self.allowed_cidrs, Unset):
            allowed_cidrs = self.allowed_cidrs

        allowed_scopes: list[str] | Unset = UNSET
        if not isinstance(self.allowed_scopes, Unset):
            allowed_scopes = self.allowed_scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rc": rc,
                "id": id,
                "key": key,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if key_prefix is not UNSET:
            field_dict["key_prefix"] = key_prefix
        if allowed_cidrs is not UNSET:
            field_dict["allowed_cidrs"] = allowed_cidrs
        if allowed_scopes is not UNSET:
            field_dict["allowed_scopes"] = allowed_scopes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        rc = d.pop("rc")

        id = UUID(d.pop("id"))

        key = d.pop("key")

        name = d.pop("name", UNSET)

        key_prefix = d.pop("key_prefix", UNSET)

        allowed_cidrs = cast(list[str], d.pop("allowed_cidrs", UNSET))

        allowed_scopes = cast(list[str], d.pop("allowed_scopes", UNSET))

        account_created_apikey = cls(
            rc=rc,
            id=id,
            key=key,
            name=name,
            key_prefix=key_prefix,
            allowed_cidrs=allowed_cidrs,
            allowed_scopes=allowed_scopes,
        )

        account_created_apikey.additional_properties = d
        return account_created_apikey

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

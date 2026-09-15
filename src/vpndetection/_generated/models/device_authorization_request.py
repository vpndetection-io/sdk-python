from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceAuthorizationRequest")


@_attrs_define
class DeviceAuthorizationRequest:
    """
    Attributes:
        client_id (str):
        scope (str | Unset): Space-delimited. Anything your client is not registered for is dropped rather than refused.
        resource (str | Unset): RFC 8707: what the token is for.
    """

    client_id: str
    scope: str | Unset = UNSET
    resource: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        scope = self.scope

        resource = self.resource

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_id": client_id,
            }
        )
        if scope is not UNSET:
            field_dict["scope"] = scope
        if resource is not UNSET:
            field_dict["resource"] = resource

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        client_id = d.pop("client_id")

        scope = d.pop("scope", UNSET)

        resource = d.pop("resource", UNSET)

        device_authorization_request = cls(
            client_id=client_id,
            scope=scope,
            resource=resource,
        )

        device_authorization_request.additional_properties = d
        return device_authorization_request

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

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClientRegistration")


@_attrs_define
class ClientRegistration:
    """
    Attributes:
        client_id (str):
        client_id_issued_at (int): Unix seconds. 64-bit, since 32 bits run out on 2038-01-19.
        client_name (str): As the person will see it.
        redirect_uris (list[str]):
        token_endpoint_auth_method (str): Always `none`.
        grant_types (list[str] | Unset): `authorization_code` and `refresh_token`.
        response_types (list[str] | Unset):
        scope (str | Unset): The most this client may be granted: `apikeys.use`.
    """

    client_id: str
    client_id_issued_at: int
    client_name: str
    redirect_uris: list[str]
    token_endpoint_auth_method: str
    grant_types: list[str] | Unset = UNSET
    response_types: list[str] | Unset = UNSET
    scope: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        client_id_issued_at = self.client_id_issued_at

        client_name = self.client_name

        redirect_uris = self.redirect_uris

        token_endpoint_auth_method = self.token_endpoint_auth_method

        grant_types: list[str] | Unset = UNSET
        if not isinstance(self.grant_types, Unset):
            grant_types = self.grant_types

        response_types: list[str] | Unset = UNSET
        if not isinstance(self.response_types, Unset):
            response_types = self.response_types

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_id": client_id,
                "client_id_issued_at": client_id_issued_at,
                "client_name": client_name,
                "redirect_uris": redirect_uris,
                "token_endpoint_auth_method": token_endpoint_auth_method,
            }
        )
        if grant_types is not UNSET:
            field_dict["grant_types"] = grant_types
        if response_types is not UNSET:
            field_dict["response_types"] = response_types
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        client_id = d.pop("client_id")

        client_id_issued_at = d.pop("client_id_issued_at")

        client_name = d.pop("client_name")

        redirect_uris = cast(list[str], d.pop("redirect_uris"))

        token_endpoint_auth_method = d.pop("token_endpoint_auth_method")

        grant_types = cast(list[str], d.pop("grant_types", UNSET))

        response_types = cast(list[str], d.pop("response_types", UNSET))

        scope = d.pop("scope", UNSET)

        client_registration = cls(
            client_id=client_id,
            client_id_issued_at=client_id_issued_at,
            client_name=client_name,
            redirect_uris=redirect_uris,
            token_endpoint_auth_method=token_endpoint_auth_method,
            grant_types=grant_types,
            response_types=response_types,
            scope=scope,
        )

        client_registration.additional_properties = d
        return client_registration

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

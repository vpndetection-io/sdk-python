from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClientRegistrationRequest")


@_attrs_define
class ClientRegistrationRequest:
    """
    Attributes:
        redirect_uris (list[str]): One to ten, each matched exactly, apart from a loopback one's port.
        client_name (str | Unset): Shown to the person as your client's own claim, marked unverified, beside where its
            redirect goes.
        grant_types (list[str] | Unset): Must include `authorization_code` when given.
        response_types (list[str] | Unset): Must include `code` when given.
        token_endpoint_auth_method (str | Unset): Read as `none`, whatever is sent.
    """

    redirect_uris: list[str]
    client_name: str | Unset = UNSET
    grant_types: list[str] | Unset = UNSET
    response_types: list[str] | Unset = UNSET
    token_endpoint_auth_method: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        redirect_uris = self.redirect_uris

        client_name = self.client_name

        grant_types: list[str] | Unset = UNSET
        if not isinstance(self.grant_types, Unset):
            grant_types = self.grant_types

        response_types: list[str] | Unset = UNSET
        if not isinstance(self.response_types, Unset):
            response_types = self.response_types

        token_endpoint_auth_method = self.token_endpoint_auth_method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "redirect_uris": redirect_uris,
            }
        )
        if client_name is not UNSET:
            field_dict["client_name"] = client_name
        if grant_types is not UNSET:
            field_dict["grant_types"] = grant_types
        if response_types is not UNSET:
            field_dict["response_types"] = response_types
        if token_endpoint_auth_method is not UNSET:
            field_dict["token_endpoint_auth_method"] = token_endpoint_auth_method

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        redirect_uris = cast(list[str], d.pop("redirect_uris"))

        client_name = d.pop("client_name", UNSET)

        grant_types = cast(list[str], d.pop("grant_types", UNSET))

        response_types = cast(list[str], d.pop("response_types", UNSET))

        token_endpoint_auth_method = d.pop("token_endpoint_auth_method", UNSET)

        client_registration_request = cls(
            redirect_uris=redirect_uris,
            client_name=client_name,
            grant_types=grant_types,
            response_types=response_types,
            token_endpoint_auth_method=token_endpoint_auth_method,
        )

        client_registration_request.additional_properties = d
        return client_registration_request

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

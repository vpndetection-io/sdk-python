from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenRequest")


@_attrs_define
class TokenRequest:
    """
    Attributes:
        grant_type (str):
        client_id (str):
        device_code (str | Unset):
        code (str | Unset):
        code_verifier (str | Unset):
        redirect_uri (str | Unset):
        refresh_token (str | Unset):
    """

    grant_type: str
    client_id: str
    device_code: str | Unset = UNSET
    code: str | Unset = UNSET
    code_verifier: str | Unset = UNSET
    redirect_uri: str | Unset = UNSET
    refresh_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        grant_type = self.grant_type

        client_id = self.client_id

        device_code = self.device_code

        code = self.code

        code_verifier = self.code_verifier

        redirect_uri = self.redirect_uri

        refresh_token = self.refresh_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
                "client_id": client_id,
            }
        )
        if device_code is not UNSET:
            field_dict["device_code"] = device_code
        if code is not UNSET:
            field_dict["code"] = code
        if code_verifier is not UNSET:
            field_dict["code_verifier"] = code_verifier
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        grant_type = d.pop("grant_type")

        client_id = d.pop("client_id")

        device_code = d.pop("device_code", UNSET)

        code = d.pop("code", UNSET)

        code_verifier = d.pop("code_verifier", UNSET)

        redirect_uri = d.pop("redirect_uri", UNSET)

        refresh_token = d.pop("refresh_token", UNSET)

        token_request = cls(
            grant_type=grant_type,
            client_id=client_id,
            device_code=device_code,
            code=code,
            code_verifier=code_verifier,
            redirect_uri=redirect_uri,
            refresh_token=refresh_token,
        )

        token_request.additional_properties = d
        return token_request

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

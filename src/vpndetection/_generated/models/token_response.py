from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenResponse")


@_attrs_define
class TokenResponse:
    """
    Attributes:
        access_token (str):
        token_type (str): Always `Bearer`.
        expires_in (int): Seconds until the access token expires.
        refresh_token (str | Unset): Always returned. A refresh consumes the token it presents, so keep this one.
        scope (str | Unset): What was actually granted, which may be narrower than what was asked for.
        mslmapikey_id (str | Unset): Not part of OAuth. The ID of the API key the person picked when they
            approved, returned by every grant while this authorization may still
            read that key back. Absent when no key was picked, or when the
            person's role no longer allows reading keys back.
        mslmapikey (str | Unset): Not part of OAuth. The API key itself, so a device ends up holding an
            ordinary key. Returned by the device code and authorization code
            grants only, never by a refresh, and only alongside
            `mslm:apikey_id`. Absent when that key's secret cannot be read back,
            which is the case for a key created before keys could be shown again
            in the console; a rotated key can be.
    """

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | Unset = UNSET
    scope: str | Unset = UNSET
    mslmapikey_id: str | Unset = UNSET
    mslmapikey: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        token_type = self.token_type

        expires_in = self.expires_in

        refresh_token = self.refresh_token

        scope = self.scope

        mslmapikey_id = self.mslmapikey_id

        mslmapikey = self.mslmapikey

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "token_type": token_type,
                "expires_in": expires_in,
            }
        )
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token
        if scope is not UNSET:
            field_dict["scope"] = scope
        if mslmapikey_id is not UNSET:
            field_dict["mslm:apikey_id"] = mslmapikey_id
        if mslmapikey is not UNSET:
            field_dict["mslm:apikey"] = mslmapikey

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        token_type = d.pop("token_type")

        expires_in = d.pop("expires_in")

        refresh_token = d.pop("refresh_token", UNSET)

        scope = d.pop("scope", UNSET)

        mslmapikey_id = d.pop("mslm:apikey_id", UNSET)

        mslmapikey = d.pop("mslm:apikey", UNSET)

        token_response = cls(
            access_token=access_token,
            token_type=token_type,
            expires_in=expires_in,
            refresh_token=refresh_token,
            scope=scope,
            mslmapikey_id=mslmapikey_id,
            mslmapikey=mslmapikey,
        )

        token_response.additional_properties = d
        return token_response

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

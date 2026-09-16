from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceAuthorization")


@_attrs_define
class DeviceAuthorization:
    """
    Attributes:
        device_code (str): Yours. Poll with it; never show it to anyone.
        user_code (str): Short and typable. This is what the person confirms.
        verification_uri (str):
        expires_in (int): Seconds until both codes expire.
        interval (int): Seconds between polls.
        verification_uri_complete (str | Unset): The same page with the code already filled in.
    """

    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    verification_uri_complete: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_code = self.device_code

        user_code = self.user_code

        verification_uri = self.verification_uri

        expires_in = self.expires_in

        interval = self.interval

        verification_uri_complete = self.verification_uri_complete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": verification_uri,
                "expires_in": expires_in,
                "interval": interval,
            }
        )
        if verification_uri_complete is not UNSET:
            field_dict["verification_uri_complete"] = verification_uri_complete

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        device_code = d.pop("device_code")

        user_code = d.pop("user_code")

        verification_uri = d.pop("verification_uri")

        expires_in = d.pop("expires_in")

        interval = d.pop("interval")

        verification_uri_complete = d.pop("verification_uri_complete", UNSET)

        device_authorization = cls(
            device_code=device_code,
            user_code=user_code,
            verification_uri=verification_uri,
            expires_in=expires_in,
            interval=interval,
            verification_uri_complete=verification_uri_complete,
        )

        device_authorization.additional_properties = d
        return device_authorization

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

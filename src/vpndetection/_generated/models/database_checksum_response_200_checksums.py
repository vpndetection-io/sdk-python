from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DatabaseChecksumResponse200Checksums")


@_attrs_define
class DatabaseChecksumResponse200Checksums:
    """
    Attributes:
        md5 (str | Unset):
        sha1 (str | Unset):
        sha256 (str | Unset):
        sha512 (str | Unset):
    """

    md5: str | Unset = UNSET
    sha1: str | Unset = UNSET
    sha256: str | Unset = UNSET
    sha512: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        md5 = self.md5

        sha1 = self.sha1

        sha256 = self.sha256

        sha512 = self.sha512

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if md5 is not UNSET:
            field_dict["md5"] = md5
        if sha1 is not UNSET:
            field_dict["sha1"] = sha1
        if sha256 is not UNSET:
            field_dict["sha256"] = sha256
        if sha512 is not UNSET:
            field_dict["sha512"] = sha512

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        md5 = d.pop("md5", UNSET)

        sha1 = d.pop("sha1", UNSET)

        sha256 = d.pop("sha256", UNSET)

        sha512 = d.pop("sha512", UNSET)

        database_checksum_response_200_checksums = cls(
            md5=md5,
            sha1=sha1,
            sha256=sha256,
            sha512=sha512,
        )

        database_checksum_response_200_checksums.additional_properties = d
        return database_checksum_response_200_checksums

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

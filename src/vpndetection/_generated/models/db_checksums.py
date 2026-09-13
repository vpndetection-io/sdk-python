from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DbChecksums")


@_attrs_define
class DbChecksums:
    """The published digests for one database file.

    Attributes:
        md5 (str):
        sha1 (str):
        sha256 (str):
        sha512 (str):
    """

    md5: str
    sha1: str
    sha256: str
    sha512: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        md5 = self.md5

        sha1 = self.sha1

        sha256 = self.sha256

        sha512 = self.sha512

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "md5": md5,
                "sha1": sha1,
                "sha256": sha256,
                "sha512": sha512,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        md5 = d.pop("md5")

        sha1 = d.pop("sha1")

        sha256 = d.pop("sha256")

        sha512 = d.pop("sha512")

        db_checksums = cls(
            md5=md5,
            sha1=sha1,
            sha256=sha256,
            sha512=sha512,
        )

        db_checksums.additional_properties = d
        return db_checksums

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

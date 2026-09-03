from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.database_checksum_response_200_checksums import (
        DatabaseChecksumResponse200Checksums,
    )


T = TypeVar("T", bound="DatabaseChecksumResponse200")


@_attrs_define
class DatabaseChecksumResponse200:
    """
    Attributes:
        id (str):
        format_ (str):
        checksums (DatabaseChecksumResponse200Checksums):
    """

    id: str
    format_: str
    checksums: DatabaseChecksumResponse200Checksums
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        format_ = self.format_

        checksums = self.checksums.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "format": format_,
                "checksums": checksums,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.database_checksum_response_200_checksums import (
            DatabaseChecksumResponse200Checksums,
        )

        d = dict(src_dict)
        id = d.pop("id")

        format_ = d.pop("format")

        checksums = DatabaseChecksumResponse200Checksums.from_dict(d.pop("checksums"))

        database_checksum_response_200 = cls(
            id=id,
            format_=format_,
            checksums=checksums,
        )

        database_checksum_response_200.additional_properties = d
        return database_checksum_response_200

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

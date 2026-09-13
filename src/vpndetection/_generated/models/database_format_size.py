from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.database_format import DatabaseFormat

T = TypeVar("T", bound="DatabaseFormatSize")


@_attrs_define
class DatabaseFormatSize:
    """
    Attributes:
        format_ (DatabaseFormat): A file format a database version is published in.
        bytes_ (int | None): Size of the published file, or null when it has not been published yet
    """

    format_: DatabaseFormat
    bytes_: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        format_ = self.format_.value

        bytes_: int | None
        bytes_ = self.bytes_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "format": format_,
                "bytes": bytes_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        format_ = DatabaseFormat(d.pop("format"))

        def _parse_bytes_(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        bytes_ = _parse_bytes_(d.pop("bytes"))

        database_format_size = cls(
            format_=format_,
            bytes_=bytes_,
        )

        database_format_size.additional_properties = d
        return database_format_size

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

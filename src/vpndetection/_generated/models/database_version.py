from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.database_format import DatabaseFormat
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.database_format_size import DatabaseFormatSize


T = TypeVar("T", bound="DatabaseVersion")


@_attrs_define
class DatabaseVersion:
    """
    Attributes:
        id (str): The versioned database id, e.g. `vpn_ip_v1`. Pass this to download. Example: vpn_ip_v1.
        version (int):  Example: 1.
        formats (list[DatabaseFormatSize]):
        summary (str | Unset):
        sample_formats (list[DatabaseFormat] | Unset): The formats an evaluation sample is published in, if any.
    """

    id: str
    version: int
    formats: list[DatabaseFormatSize]
    summary: str | Unset = UNSET
    sample_formats: list[DatabaseFormat] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        version = self.version

        formats = []
        for formats_item_data in self.formats:
            formats_item = formats_item_data.to_dict()
            formats.append(formats_item)

        summary = self.summary

        sample_formats: list[str] | Unset = UNSET
        if not isinstance(self.sample_formats, Unset):
            sample_formats = []
            for sample_formats_item_data in self.sample_formats:
                sample_formats_item = sample_formats_item_data.value
                sample_formats.append(sample_formats_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "version": version,
                "formats": formats,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if sample_formats is not UNSET:
            field_dict["sample_formats"] = sample_formats

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.database_format_size import DatabaseFormatSize

        d = dict(src_dict)
        id = d.pop("id")

        version = d.pop("version")

        formats = []
        _formats = d.pop("formats")
        for formats_item_data in _formats:
            formats_item = DatabaseFormatSize.from_dict(formats_item_data)

            formats.append(formats_item)

        summary = d.pop("summary", UNSET)

        _sample_formats = d.pop("sample_formats", UNSET)
        sample_formats: list[DatabaseFormat] | Unset = UNSET
        if _sample_formats is not UNSET:
            sample_formats = []
            for sample_formats_item_data in _sample_formats:
                sample_formats_item = DatabaseFormat(sample_formats_item_data)

                sample_formats.append(sample_formats_item)

        database_version = cls(
            id=id,
            version=version,
            formats=formats,
            summary=summary,
            sample_formats=sample_formats,
        )

        database_version.additional_properties = d
        return database_version

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

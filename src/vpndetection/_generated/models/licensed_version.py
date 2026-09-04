from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.licensed_version_sample_formats_item import LicensedVersionSampleFormatsItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_format_size import DatasetFormatSize


T = TypeVar("T", bound="LicensedVersion")


@_attrs_define
class LicensedVersion:
    """
    Attributes:
        id (str): The versioned dataset id, e.g. `vpn_ip_v1`. Pass this to download. Example: vpn_ip_v1.
        version (int):  Example: 1.
        formats (list[DatasetFormatSize]):
        summary (str | Unset):
        sample_formats (list[LicensedVersionSampleFormatsItem] | Unset): The formats an evaluation sample is published
            in, if any.
    """

    id: str
    version: int
    formats: list[DatasetFormatSize]
    summary: str | Unset = UNSET
    sample_formats: list[LicensedVersionSampleFormatsItem] | Unset = UNSET
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
            field_dict["sampleFormats"] = sample_formats

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.dataset_format_size import DatasetFormatSize

        d = dict(src_dict)
        id = d.pop("id")

        version = d.pop("version")

        formats = []
        _formats = d.pop("formats")
        for formats_item_data in _formats:
            formats_item = DatasetFormatSize.from_dict(formats_item_data)

            formats.append(formats_item)

        summary = d.pop("summary", UNSET)

        _sample_formats = d.pop("sampleFormats", UNSET)
        sample_formats: list[LicensedVersionSampleFormatsItem] | Unset = UNSET
        if _sample_formats is not UNSET:
            sample_formats = []
            for sample_formats_item_data in _sample_formats:
                sample_formats_item = LicensedVersionSampleFormatsItem(sample_formats_item_data)

                sample_formats.append(sample_formats_item)

        licensed_version = cls(
            id=id,
            version=version,
            formats=formats,
            summary=summary,
            sample_formats=sample_formats,
        )

        licensed_version.additional_properties = d
        return licensed_version

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

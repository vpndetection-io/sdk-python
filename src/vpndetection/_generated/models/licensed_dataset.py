from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.licensed_dataset_redistribution import LicensedDatasetRedistribution
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_format_size import DatasetFormatSize


T = TypeVar("T", bound="LicensedDataset")


@_attrs_define
class LicensedDataset:
    """
    Attributes:
        id (str):
        name (str):
        redistribution (LicensedDatasetRedistribution): What your license permits you to do with the data
        in_term (bool): False when the license has lapsed; downloads are refused
        formats (list[DatasetFormatSize]):
        summary (str | Unset):
        retired (bool | Unset): Licensed but no longer published. Talk to us.
        starts (datetime.datetime | Unset):
        expires (datetime.datetime | None | Unset):
    """

    id: str
    name: str
    redistribution: LicensedDatasetRedistribution
    in_term: bool
    formats: list[DatasetFormatSize]
    summary: str | Unset = UNSET
    retired: bool | Unset = UNSET
    starts: datetime.datetime | Unset = UNSET
    expires: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        redistribution = self.redistribution.value

        in_term = self.in_term

        formats = []
        for formats_item_data in self.formats:
            formats_item = formats_item_data.to_dict()
            formats.append(formats_item)

        summary = self.summary

        retired = self.retired

        starts: str | Unset = UNSET
        if not isinstance(self.starts, Unset):
            starts = self.starts.isoformat()

        expires: None | str | Unset
        if isinstance(self.expires, Unset):
            expires = UNSET
        elif isinstance(self.expires, datetime.datetime):
            expires = self.expires.isoformat()
        else:
            expires = self.expires

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "redistribution": redistribution,
                "in_term": in_term,
                "formats": formats,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if retired is not UNSET:
            field_dict["retired"] = retired
        if starts is not UNSET:
            field_dict["starts"] = starts
        if expires is not UNSET:
            field_dict["expires"] = expires

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.dataset_format_size import DatasetFormatSize

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        redistribution = LicensedDatasetRedistribution(d.pop("redistribution"))

        in_term = d.pop("in_term")

        formats = []
        _formats = d.pop("formats")
        for formats_item_data in _formats:
            formats_item = DatasetFormatSize.from_dict(formats_item_data)

            formats.append(formats_item)

        summary = d.pop("summary", UNSET)

        retired = d.pop("retired", UNSET)

        _starts = d.pop("starts", UNSET)
        starts: datetime.datetime | Unset
        if isinstance(_starts, Unset):
            starts = UNSET
        else:
            starts = datetime.datetime.fromisoformat(_starts)

        def _parse_expires(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_type_0 = datetime.datetime.fromisoformat(data)

                return expires_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires = _parse_expires(d.pop("expires", UNSET))

        licensed_dataset = cls(
            id=id,
            name=name,
            redistribution=redistribution,
            in_term=in_term,
            formats=formats,
            summary=summary,
            retired=retired,
            starts=starts,
            expires=expires,
        )

        licensed_dataset.additional_properties = d
        return licensed_dataset

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

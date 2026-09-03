from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_metadata_sample import DatasetMetadataSample
    from ..models.dataset_metadata_schema import DatasetMetadataSchema
    from ..models.dataset_metadata_size import DatasetMetadataSize


T = TypeVar("T", bound="DatasetMetadata")


@_attrs_define
class DatasetMetadata:
    """
    Attributes:
        id (str):
        updated (datetime.date):
        entries (int): Row count in the current build
        schema (DatasetMetadataSchema): Columns, keyed by format
        update_freq (str | Unset): How often a new build is published
        sample (DatasetMetadataSample | Unset): A few real rows, keyed by format
        size (DatasetMetadataSize | Unset): Bytes per format
    """

    id: str
    updated: datetime.date
    entries: int
    schema: DatasetMetadataSchema
    update_freq: str | Unset = UNSET
    sample: DatasetMetadataSample | Unset = UNSET
    size: DatasetMetadataSize | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        updated = self.updated.isoformat()

        entries = self.entries

        schema = self.schema.to_dict()

        update_freq = self.update_freq

        sample: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sample, Unset):
            sample = self.sample.to_dict()

        size: dict[str, Any] | Unset = UNSET
        if not isinstance(self.size, Unset):
            size = self.size.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "updated": updated,
                "entries": entries,
                "schema": schema,
            }
        )
        if update_freq is not UNSET:
            field_dict["update_freq"] = update_freq
        if sample is not UNSET:
            field_dict["sample"] = sample
        if size is not UNSET:
            field_dict["size"] = size

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.dataset_metadata_sample import DatasetMetadataSample
        from ..models.dataset_metadata_schema import DatasetMetadataSchema
        from ..models.dataset_metadata_size import DatasetMetadataSize

        d = dict(src_dict)
        id = d.pop("id")

        updated = datetime.date.fromisoformat(d.pop("updated"))

        entries = d.pop("entries")

        schema = DatasetMetadataSchema.from_dict(d.pop("schema"))

        update_freq = d.pop("update_freq", UNSET)

        _sample = d.pop("sample", UNSET)
        sample: DatasetMetadataSample | Unset
        if isinstance(_sample, Unset):
            sample = UNSET
        else:
            sample = DatasetMetadataSample.from_dict(_sample)

        _size = d.pop("size", UNSET)
        size: DatasetMetadataSize | Unset
        if isinstance(_size, Unset):
            size = UNSET
        else:
            size = DatasetMetadataSize.from_dict(_size)

        dataset_metadata = cls(
            id=id,
            updated=updated,
            entries=entries,
            schema=schema,
            update_freq=update_freq,
            sample=sample,
            size=size,
        )

        dataset_metadata.additional_properties = d
        return dataset_metadata

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

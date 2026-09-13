from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.database_metadata_sample import DatabaseMetadataSample
    from ..models.database_metadata_sample_size import DatabaseMetadataSampleSize
    from ..models.database_metadata_schema import DatabaseMetadataSchema
    from ..models.database_metadata_size import DatabaseMetadataSize


T = TypeVar("T", bound="DatabaseMetadata")


@_attrs_define
class DatabaseMetadata:
    """
    Attributes:
        id (str):
        updated (datetime.date):
        entries (int): Row count in the current build
        schema (DatabaseMetadataSchema): Columns, keyed by format
        update_freq (str | Unset): How often a new build is published
        sample (DatabaseMetadataSample | Unset): A few real rows, keyed by format
        size (DatabaseMetadataSize | Unset): Bytes per format
        sample_size (DatabaseMetadataSampleSize | Unset): Bytes per format of the evaluation sample, where one is
            published
        sample_entries (int | Unset): Row count in the evaluation sample
    """

    id: str
    updated: datetime.date
    entries: int
    schema: DatabaseMetadataSchema
    update_freq: str | Unset = UNSET
    sample: DatabaseMetadataSample | Unset = UNSET
    size: DatabaseMetadataSize | Unset = UNSET
    sample_size: DatabaseMetadataSampleSize | Unset = UNSET
    sample_entries: int | Unset = UNSET
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

        sample_size: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sample_size, Unset):
            sample_size = self.sample_size.to_dict()

        sample_entries = self.sample_entries

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
        if sample_size is not UNSET:
            field_dict["sample_size"] = sample_size
        if sample_entries is not UNSET:
            field_dict["sample_entries"] = sample_entries

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.database_metadata_sample import DatabaseMetadataSample
        from ..models.database_metadata_sample_size import (
            DatabaseMetadataSampleSize,
        )
        from ..models.database_metadata_schema import DatabaseMetadataSchema
        from ..models.database_metadata_size import DatabaseMetadataSize

        d = dict(src_dict)
        id = d.pop("id")

        updated = datetime.date.fromisoformat(d.pop("updated"))

        entries = d.pop("entries")

        schema = DatabaseMetadataSchema.from_dict(d.pop("schema"))

        update_freq = d.pop("update_freq", UNSET)

        _sample = d.pop("sample", UNSET)
        sample: DatabaseMetadataSample | Unset
        if isinstance(_sample, Unset):
            sample = UNSET
        else:
            sample = DatabaseMetadataSample.from_dict(_sample)

        _size = d.pop("size", UNSET)
        size: DatabaseMetadataSize | Unset
        if isinstance(_size, Unset):
            size = UNSET
        else:
            size = DatabaseMetadataSize.from_dict(_size)

        _sample_size = d.pop("sample_size", UNSET)
        sample_size: DatabaseMetadataSampleSize | Unset
        if isinstance(_sample_size, Unset):
            sample_size = UNSET
        else:
            sample_size = DatabaseMetadataSampleSize.from_dict(_sample_size)

        sample_entries = d.pop("sample_entries", UNSET)

        database_metadata = cls(
            id=id,
            updated=updated,
            entries=entries,
            schema=schema,
            update_freq=update_freq,
            sample=sample,
            size=size,
            sample_size=sample_size,
            sample_entries=sample_entries,
        )

        database_metadata.additional_properties = d
        return database_metadata

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

from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.download_outcome import DownloadOutcome
from ..types import UNSET, Unset

T = TypeVar("T", bound="Download")


@_attrs_define
class Download:
    """
    Attributes:
        dataset_id (str):
        format_ (str):
        outcome (DownloadOutcome):
        created (datetime.datetime):
        bytes_ (int | None | Unset):
    """

    dataset_id: str
    format_: str
    outcome: DownloadOutcome
    created: datetime.datetime
    bytes_: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        format_ = self.format_

        outcome = self.outcome.value

        created = self.created.isoformat()

        bytes_: int | None | Unset
        if isinstance(self.bytes_, Unset):
            bytes_ = UNSET
        else:
            bytes_ = self.bytes_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_id": dataset_id,
                "format": format_,
                "outcome": outcome,
                "created": created,
            }
        )
        if bytes_ is not UNSET:
            field_dict["bytes"] = bytes_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        dataset_id = d.pop("dataset_id")

        format_ = d.pop("format")

        outcome = DownloadOutcome(d.pop("outcome"))

        created = datetime.datetime.fromisoformat(d.pop("created"))

        def _parse_bytes_(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        bytes_ = _parse_bytes_(d.pop("bytes", UNSET))

        download = cls(
            dataset_id=dataset_id,
            format_=format_,
            outcome=outcome,
            created=created,
            bytes_=bytes_,
        )

        download.additional_properties = d
        return download

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

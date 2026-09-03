from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassDetail")


@_attrs_define
class ClassDetail:
    """The shared detail shape for the hosting, relay, tor and cdn datasets.
    Every key is present when the object is populated; the object is `{}`
    when its flag is false.

        Attributes:
            provider (str | Unset): The provider, or an empty string where the dataset has none. Example: M247.
            confidence (str | Unset): How strongly the classification is supported. Example: high.
            last_seen (datetime.date | Unset): The most recent date this address was observed in this dataset. Example:
                2026-09-02.
    """

    provider: str | Unset = UNSET
    confidence: str | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        confidence = self.confidence

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        provider = d.pop("provider", UNSET)

        confidence = d.pop("confidence", UNSET)

        _last_seen = d.pop("last_seen", UNSET)
        last_seen: datetime.date | Unset
        if isinstance(_last_seen, Unset):
            last_seen = UNSET
        else:
            last_seen = datetime.date.fromisoformat(_last_seen)

        class_detail = cls(
            provider=provider,
            confidence=confidence,
            last_seen=last_seen,
        )

        class_detail.additional_properties = d
        return class_detail

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

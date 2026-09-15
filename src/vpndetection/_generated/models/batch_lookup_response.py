from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.batch_lookup_response_errors import BatchLookupResponseErrors
    from ..models.batch_lookup_response_results import BatchLookupResponseResults


T = TypeVar("T", bound="BatchLookupResponse")


@_attrs_define
class BatchLookupResponse:
    """
    Attributes:
        results (BatchLookupResponseResults): One answer per input string that was classified, keyed by the string
            as you sent it; the `ip` inside is the normalized form. Each value is
            exactly what `GET /{ip}` answers for your plan.
        errors (BatchLookupResponseErrors): One entry per input string that could not be classified, keyed the
            same way. Empty when every entry was answered.
    """

    results: BatchLookupResponseResults
    errors: BatchLookupResponseErrors
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = self.results.to_dict()

        errors = self.errors.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.batch_lookup_response_errors import BatchLookupResponseErrors
        from ..models.batch_lookup_response_results import (
            BatchLookupResponseResults,
        )

        d = dict(src_dict)
        results = BatchLookupResponseResults.from_dict(d.pop("results"))

        errors = BatchLookupResponseErrors.from_dict(d.pop("errors"))

        batch_lookup_response = cls(
            results=results,
            errors=errors,
        )

        batch_lookup_response.additional_properties = d
        return batch_lookup_response

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

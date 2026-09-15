from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BatchLookupError")


@_attrs_define
class BatchLookupError:
    """Why one entry of a batch was not answered, as the single lookup would have reported it.

    Attributes:
        status (int): The HTTP status `GET /{ip}` would have answered for this entry: `400`
            for a string that is not an address, `429` for a spent allowance,
            `500` when the VPN dataset could not be consulted. A `429` here is
            never a throttle; the whole call is refused instead.
             Example: 400.
        error (str): The same message the single lookup carries for that status. Example: not a valid IP address.
    """

    status: int
    error: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "error": error,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        status = d.pop("status")

        error = d.pop("error")

        batch_lookup_error = cls(
            status=status,
            error=error,
        )

        batch_lookup_error.additional_properties = d
        return batch_lookup_error

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

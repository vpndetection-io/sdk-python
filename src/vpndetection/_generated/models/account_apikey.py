from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AccountApikey")


@_attrs_define
class AccountApikey:
    """The credential itself. The key is never echoed - only its id, which is
    what the console shows and what you can act on.

        Attributes:
            id (UUID):
            expires (datetime.datetime | None): Null for a key with no end date, which is the normal case.
            allowed_cidrs (list[str]): The source addresses this key may be used from. EMPTY means
                unrestricted, never "deny all".
    """

    id: UUID
    expires: datetime.datetime | None
    allowed_cidrs: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        expires: None | str
        if isinstance(self.expires, datetime.datetime):
            expires = self.expires.isoformat()
        else:
            expires = self.expires

        allowed_cidrs = self.allowed_cidrs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "expires": expires,
                "allowed_cidrs": allowed_cidrs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        def _parse_expires(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_type_0 = datetime.datetime.fromisoformat(data)

                return expires_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        expires = _parse_expires(d.pop("expires"))

        allowed_cidrs = cast(list[str], d.pop("allowed_cidrs"))

        account_apikey = cls(
            id=id,
            expires=expires,
            allowed_cidrs=allowed_cidrs,
        )

        account_apikey.additional_properties = d
        return account_apikey

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

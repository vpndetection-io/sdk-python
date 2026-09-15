from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApikeyDetail")


@_attrs_define
class ApikeyDetail:
    """Key METADATA. Never the key itself.

    Attributes:
        id (UUID):
        name (str):
        key_prefix (str): The leading, non-secret part, so a key is recognisable without storing it.
        created (datetime.datetime):
        expires (datetime.datetime | None | Unset):
        last_used_at (datetime.datetime | None | Unset):
        revoked_at (datetime.datetime | None | Unset):
        allowed_cidrs (list[str] | Unset): Source-IP allowlist. EMPTY MEANS UNRESTRICTED, not deny-all.
        allowed_scopes (list[str] | Unset):
        retrievable (bool | Unset): Whether this key's secret can still be read back. False permanently for a key issued
            before secrets were stored recoverably.
    """

    id: UUID
    name: str
    key_prefix: str
    created: datetime.datetime
    expires: datetime.datetime | None | Unset = UNSET
    last_used_at: datetime.datetime | None | Unset = UNSET
    revoked_at: datetime.datetime | None | Unset = UNSET
    allowed_cidrs: list[str] | Unset = UNSET
    allowed_scopes: list[str] | Unset = UNSET
    retrievable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        name = self.name

        key_prefix = self.key_prefix

        created = self.created.isoformat()

        expires: None | str | Unset
        if isinstance(self.expires, Unset):
            expires = UNSET
        elif isinstance(self.expires, datetime.datetime):
            expires = self.expires.isoformat()
        else:
            expires = self.expires

        last_used_at: None | str | Unset
        if isinstance(self.last_used_at, Unset):
            last_used_at = UNSET
        elif isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        revoked_at: None | str | Unset
        if isinstance(self.revoked_at, Unset):
            revoked_at = UNSET
        elif isinstance(self.revoked_at, datetime.datetime):
            revoked_at = self.revoked_at.isoformat()
        else:
            revoked_at = self.revoked_at

        allowed_cidrs: list[str] | Unset = UNSET
        if not isinstance(self.allowed_cidrs, Unset):
            allowed_cidrs = self.allowed_cidrs

        allowed_scopes: list[str] | Unset = UNSET
        if not isinstance(self.allowed_scopes, Unset):
            allowed_scopes = self.allowed_scopes

        retrievable = self.retrievable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "key_prefix": key_prefix,
                "created": created,
            }
        )
        if expires is not UNSET:
            field_dict["expires"] = expires
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at
        if revoked_at is not UNSET:
            field_dict["revoked_at"] = revoked_at
        if allowed_cidrs is not UNSET:
            field_dict["allowed_cidrs"] = allowed_cidrs
        if allowed_scopes is not UNSET:
            field_dict["allowed_scopes"] = allowed_scopes
        if retrievable is not UNSET:
            field_dict["retrievable"] = retrievable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = UUID(d.pop("id"))

        name = d.pop("name")

        key_prefix = d.pop("key_prefix")

        created = datetime.datetime.fromisoformat(d.pop("created"))

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

        def _parse_last_used_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = datetime.datetime.fromisoformat(data)

                return last_used_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at", UNSET))

        def _parse_revoked_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revoked_at_type_0 = datetime.datetime.fromisoformat(data)

                return revoked_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        revoked_at = _parse_revoked_at(d.pop("revoked_at", UNSET))

        allowed_cidrs = cast(list[str], d.pop("allowed_cidrs", UNSET))

        allowed_scopes = cast(list[str], d.pop("allowed_scopes", UNSET))

        retrievable = d.pop("retrievable", UNSET)

        apikey_detail = cls(
            id=id,
            name=name,
            key_prefix=key_prefix,
            created=created,
            expires=expires,
            last_used_at=last_used_at,
            revoked_at=revoked_at,
            allowed_cidrs=allowed_cidrs,
            allowed_scopes=allowed_scopes,
            retrievable=retrievable,
        )

        apikey_detail.additional_properties = d
        return apikey_detail

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

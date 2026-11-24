from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SmtpDetail")


@_attrs_define
class SmtpDetail:
    """The mail server that answered on the address, from our SMTP IP database.
    Every key is present when the object is populated; the object is `{}`
    when `is_smtp` is false.

        Attributes:
            port (int | Unset): The port the server answered on. Example: 25.
            banner (str | Unset): Its banner. Example: 220 mail.example.com ESMTP Postfix.
            session_ok (bool | Unset): A session was set up. Example: True.
            first_seen (datetime.date | Unset): The first day it answered. Example: 2026-08-04.
            last_seen (datetime.date | Unset): The last day it did. Example: 2026-11-15.
    """

    port: int | Unset = UNSET
    banner: str | Unset = UNSET
    session_ok: bool | Unset = UNSET
    first_seen: datetime.date | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        port = self.port

        banner = self.banner

        session_ok = self.session_ok

        first_seen: str | Unset = UNSET
        if not isinstance(self.first_seen, Unset):
            first_seen = self.first_seen.isoformat()

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if port is not UNSET:
            field_dict["port"] = port
        if banner is not UNSET:
            field_dict["banner"] = banner
        if session_ok is not UNSET:
            field_dict["session_ok"] = session_ok
        if first_seen is not UNSET:
            field_dict["first_seen"] = first_seen
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        port = d.pop("port", UNSET)

        banner = d.pop("banner", UNSET)

        session_ok = d.pop("session_ok", UNSET)

        _first_seen = d.pop("first_seen", UNSET)
        first_seen: datetime.date | Unset
        if isinstance(_first_seen, Unset):
            first_seen = UNSET
        else:
            first_seen = datetime.date.fromisoformat(_first_seen)

        _last_seen = d.pop("last_seen", UNSET)
        last_seen: datetime.date | Unset
        if isinstance(_last_seen, Unset):
            last_seen = UNSET
        else:
            last_seen = datetime.date.fromisoformat(_last_seen)

        smtp_detail = cls(
            port=port,
            banner=banner,
            session_ok=session_ok,
            first_seen=first_seen,
            last_seen=last_seen,
        )

        smtp_detail.additional_properties = d
        return smtp_detail

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

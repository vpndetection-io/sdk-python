from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SshDetail")


@_attrs_define
class SshDetail:
    """The SSH server that answered on the address, from our SSH IP database.
    Every key is present when the object is populated; the object is `{}`
    when `is_ssh` is false.

        Attributes:
            port (int | Unset): The port the server answered on. Example: 22.
            banner (str | Unset): Its banner. Example: SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.5.
            host_key_fp (str | Unset): Its host key's fingerprint. Example:
                SHA256:9Bq3Jrm6pVJ7QqV2c8l0pE6f8wJ4sZ4u5tYyH9cXo1E.
            session_ok (bool | Unset): A session was set up. Example: True.
            first_seen (str | Unset): The first day it answered. Example: 2026-08-04.
            last_seen (str | Unset): The last day it did. Example: 2026-11-15.
    """

    port: int | Unset = UNSET
    banner: str | Unset = UNSET
    host_key_fp: str | Unset = UNSET
    session_ok: bool | Unset = UNSET
    first_seen: str | Unset = UNSET
    last_seen: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        port = self.port

        banner = self.banner

        host_key_fp = self.host_key_fp

        session_ok = self.session_ok

        first_seen = self.first_seen

        last_seen = self.last_seen

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if port is not UNSET:
            field_dict["port"] = port
        if banner is not UNSET:
            field_dict["banner"] = banner
        if host_key_fp is not UNSET:
            field_dict["host_key_fp"] = host_key_fp
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

        host_key_fp = d.pop("host_key_fp", UNSET)

        session_ok = d.pop("session_ok", UNSET)

        first_seen = d.pop("first_seen", UNSET)

        last_seen = d.pop("last_seen", UNSET)

        ssh_detail = cls(
            port=port,
            banner=banner,
            host_key_fp=host_key_fp,
            session_ok=session_ok,
            first_seen=first_seen,
            last_seen=last_seen,
        )

        ssh_detail.additional_properties = d
        return ssh_detail

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

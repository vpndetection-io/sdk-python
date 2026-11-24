from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WebDetail")


@_attrs_define
class WebDetail:
    """One port of the address that answered as a web server, from our Web IP database.

    Attributes:
        port (int): 80 or 443. Example: 443.
        tls_ok (bool): A TLS handshake completed. Example: True.
        session_ok (bool): An HTTP response came back. Example: True.
        status_code (int): Its status, 0 where none came. Example: 200.
        server (str): Its `Server` header. Example: nginx.
        location (str): Where it redirected.
        title (str): The page's title. Example: Welcome to nginx!.
        cert_subject_cn (str): The certificate's subject common name. Example: example.com.
        cert_subject_o (str): Its subject organization.
        cert_issuer_dn (str): Its issuer. Example: CN=R11,O=Let's Encrypt,C=US.
        cert_browser_trusted (bool): Browsers trust it. Example: True.
        tls_version (str): The TLS version negotiated, empty without TLS. Example: TLS 1.3.
        first_seen (datetime.date): The first day the port was open. Example: 2026-08-04.
        last_seen (datetime.date): The last day it was. Example: 2026-11-15.
    """

    port: int
    tls_ok: bool
    session_ok: bool
    status_code: int
    server: str
    location: str
    title: str
    cert_subject_cn: str
    cert_subject_o: str
    cert_issuer_dn: str
    cert_browser_trusted: bool
    tls_version: str
    first_seen: datetime.date
    last_seen: datetime.date
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        port = self.port

        tls_ok = self.tls_ok

        session_ok = self.session_ok

        status_code = self.status_code

        server = self.server

        location = self.location

        title = self.title

        cert_subject_cn = self.cert_subject_cn

        cert_subject_o = self.cert_subject_o

        cert_issuer_dn = self.cert_issuer_dn

        cert_browser_trusted = self.cert_browser_trusted

        tls_version = self.tls_version

        first_seen = self.first_seen.isoformat()

        last_seen = self.last_seen.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "port": port,
                "tls_ok": tls_ok,
                "session_ok": session_ok,
                "status_code": status_code,
                "server": server,
                "location": location,
                "title": title,
                "cert_subject_cn": cert_subject_cn,
                "cert_subject_o": cert_subject_o,
                "cert_issuer_dn": cert_issuer_dn,
                "cert_browser_trusted": cert_browser_trusted,
                "tls_version": tls_version,
                "first_seen": first_seen,
                "last_seen": last_seen,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        port = d.pop("port")

        tls_ok = d.pop("tls_ok")

        session_ok = d.pop("session_ok")

        status_code = d.pop("status_code")

        server = d.pop("server")

        location = d.pop("location")

        title = d.pop("title")

        cert_subject_cn = d.pop("cert_subject_cn")

        cert_subject_o = d.pop("cert_subject_o")

        cert_issuer_dn = d.pop("cert_issuer_dn")

        cert_browser_trusted = d.pop("cert_browser_trusted")

        tls_version = d.pop("tls_version")

        first_seen = datetime.date.fromisoformat(d.pop("first_seen"))

        last_seen = datetime.date.fromisoformat(d.pop("last_seen"))

        web_detail = cls(
            port=port,
            tls_ok=tls_ok,
            session_ok=session_ok,
            status_code=status_code,
            server=server,
            location=location,
            title=title,
            cert_subject_cn=cert_subject_cn,
            cert_subject_o=cert_subject_o,
            cert_issuer_dn=cert_issuer_dn,
            cert_browser_trusted=cert_browser_trusted,
            tls_version=tls_version,
            first_seen=first_seen,
            last_seen=last_seen,
        )

        web_detail.additional_properties = d
        return web_detail

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

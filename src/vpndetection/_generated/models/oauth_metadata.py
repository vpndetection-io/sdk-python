from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OauthMetadata")


@_attrs_define
class OauthMetadata:
    """
    Attributes:
        issuer (str):
        authorization_endpoint (str):
        token_endpoint (str):
        device_authorization_endpoint (str | Unset):
        revocation_endpoint (str | Unset):
        scopes_supported (list[str] | Unset):
        response_types_supported (list[str] | Unset):
        grant_types_supported (list[str] | Unset):
        code_challenge_methods_supported (list[str] | Unset):
        client_id_metadata_document_supported (bool | Unset): A client_id may be an https URL serving your client
            metadata.
    """

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    device_authorization_endpoint: str | Unset = UNSET
    revocation_endpoint: str | Unset = UNSET
    scopes_supported: list[str] | Unset = UNSET
    response_types_supported: list[str] | Unset = UNSET
    grant_types_supported: list[str] | Unset = UNSET
    code_challenge_methods_supported: list[str] | Unset = UNSET
    client_id_metadata_document_supported: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issuer = self.issuer

        authorization_endpoint = self.authorization_endpoint

        token_endpoint = self.token_endpoint

        device_authorization_endpoint = self.device_authorization_endpoint

        revocation_endpoint = self.revocation_endpoint

        scopes_supported: list[str] | Unset = UNSET
        if not isinstance(self.scopes_supported, Unset):
            scopes_supported = self.scopes_supported

        response_types_supported: list[str] | Unset = UNSET
        if not isinstance(self.response_types_supported, Unset):
            response_types_supported = self.response_types_supported

        grant_types_supported: list[str] | Unset = UNSET
        if not isinstance(self.grant_types_supported, Unset):
            grant_types_supported = self.grant_types_supported

        code_challenge_methods_supported: list[str] | Unset = UNSET
        if not isinstance(self.code_challenge_methods_supported, Unset):
            code_challenge_methods_supported = self.code_challenge_methods_supported

        client_id_metadata_document_supported = self.client_id_metadata_document_supported

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "issuer": issuer,
                "authorization_endpoint": authorization_endpoint,
                "token_endpoint": token_endpoint,
            }
        )
        if device_authorization_endpoint is not UNSET:
            field_dict["device_authorization_endpoint"] = device_authorization_endpoint
        if revocation_endpoint is not UNSET:
            field_dict["revocation_endpoint"] = revocation_endpoint
        if scopes_supported is not UNSET:
            field_dict["scopes_supported"] = scopes_supported
        if response_types_supported is not UNSET:
            field_dict["response_types_supported"] = response_types_supported
        if grant_types_supported is not UNSET:
            field_dict["grant_types_supported"] = grant_types_supported
        if code_challenge_methods_supported is not UNSET:
            field_dict["code_challenge_methods_supported"] = code_challenge_methods_supported
        if client_id_metadata_document_supported is not UNSET:
            field_dict["client_id_metadata_document_supported"] = (
                client_id_metadata_document_supported
            )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        issuer = d.pop("issuer")

        authorization_endpoint = d.pop("authorization_endpoint")

        token_endpoint = d.pop("token_endpoint")

        device_authorization_endpoint = d.pop("device_authorization_endpoint", UNSET)

        revocation_endpoint = d.pop("revocation_endpoint", UNSET)

        scopes_supported = cast(list[str], d.pop("scopes_supported", UNSET))

        response_types_supported = cast(list[str], d.pop("response_types_supported", UNSET))

        grant_types_supported = cast(list[str], d.pop("grant_types_supported", UNSET))

        code_challenge_methods_supported = cast(
            list[str], d.pop("code_challenge_methods_supported", UNSET)
        )

        client_id_metadata_document_supported = d.pop(
            "client_id_metadata_document_supported", UNSET
        )

        oauth_metadata = cls(
            issuer=issuer,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            device_authorization_endpoint=device_authorization_endpoint,
            revocation_endpoint=revocation_endpoint,
            scopes_supported=scopes_supported,
            response_types_supported=response_types_supported,
            grant_types_supported=grant_types_supported,
            code_challenge_methods_supported=code_challenge_methods_supported,
            client_id_metadata_document_supported=client_id_metadata_document_supported,
        )

        oauth_metadata.additional_properties = d
        return oauth_metadata

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

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.account_org_ref import AccountOrgRef
    from ..models.account_user import AccountUser


T = TypeVar("T", bound="Identity")


@_attrs_define
class Identity:
    """
    Attributes:
        rc (str):
        user (AccountUser):
        org (AccountOrgRef):
        scopes (list[str]): What this credential may do right now.
    """

    rc: str
    user: AccountUser
    org: AccountOrgRef
    scopes: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rc = self.rc

        user = self.user.to_dict()

        org = self.org.to_dict()

        scopes = self.scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rc": rc,
                "user": user,
                "org": org,
                "scopes": scopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.account_org_ref import AccountOrgRef
        from ..models.account_user import AccountUser

        d = dict(src_dict)
        rc = d.pop("rc")

        user = AccountUser.from_dict(d.pop("user"))

        org = AccountOrgRef.from_dict(d.pop("org"))

        scopes = cast(list[str], d.pop("scopes"))

        identity = cls(
            rc=rc,
            user=user,
            org=org,
            scopes=scopes,
        )

        identity.additional_properties = d
        return identity

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

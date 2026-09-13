from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.account_apikey import AccountApikey
    from ..models.account_plan import AccountPlan
    from ..models.account_usage import AccountUsage


T = TypeVar("T", bound="AccountMe")


@_attrs_define
class AccountMe:
    """
    Attributes:
        org_id (UUID): The organization the key belongs to.
        apikey (AccountApikey): The credential itself. The key is never echoed - only its id, which is
            what the console shows and what you can act on.
        plan (AccountPlan):
        usage (AccountUsage):
    """

    org_id: UUID
    apikey: AccountApikey
    plan: AccountPlan
    usage: AccountUsage
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        org_id = str(self.org_id)

        apikey = self.apikey.to_dict()

        plan = self.plan.to_dict()

        usage = self.usage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "org_id": org_id,
                "apikey": apikey,
                "plan": plan,
                "usage": usage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.account_apikey import AccountApikey
        from ..models.account_plan import AccountPlan
        from ..models.account_usage import AccountUsage

        d = dict(src_dict)
        org_id = UUID(d.pop("org_id"))

        apikey = AccountApikey.from_dict(d.pop("apikey"))

        plan = AccountPlan.from_dict(d.pop("plan"))

        usage = AccountUsage.from_dict(d.pop("usage"))

        account_me = cls(
            org_id=org_id,
            apikey=apikey,
            plan=plan,
            usage=usage,
        )

        account_me.additional_properties = d
        return account_me

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

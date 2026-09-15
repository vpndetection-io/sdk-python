from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.entitlement_plan_tier import EntitlementPlanTier

T = TypeVar("T", bound="EntitlementPlan")


@_attrs_define
class EntitlementPlan:
    """
    Attributes:
        key (str): The plan the organization is on. Example: max.
        tier (EntitlementPlanTier): The field tier, which decides how much of a lookup answer comes
            back. What each tier includes is documented on the lookup endpoint
            rather than repeated here, so there is one place it can be wrong.
    """

    key: str
    tier: EntitlementPlanTier
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        tier = self.tier.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "tier": tier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        key = d.pop("key")

        tier = EntitlementPlanTier(d.pop("tier"))

        entitlement_plan = cls(
            key=key,
            tier=tier,
        )

        entitlement_plan.additional_properties = d
        return entitlement_plan

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

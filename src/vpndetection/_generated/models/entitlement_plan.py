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
        key (str): The plan the organization is on, as an identifier that is never
            renamed or reused: `free` for the free plan, or a paid plan's key.
            Compare against it and show `name`. On `free`, usage counts the
            day's lookups answered with every field, its daily trial.
             Example: max.
        name (str): The plan's name, as the site and console show it: `Unlimited` for
            the free plan. Show this rather than a name built from `key`: a
            plan's name can change, and its key never does.
             Example: Max.
        tier (EntitlementPlanTier): The field tier, which decides how much of a lookup answer comes
            back; `free` is the free plan's. This list never gains a value: a
            new plan reports one of these. What each tier includes is documented
            on the lookup endpoint rather than repeated here, so there is one
            place it can be wrong.
    """

    key: str
    name: str
    tier: EntitlementPlanTier
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        name = self.name

        tier = self.tier.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "name": name,
                "tier": tier,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        key = d.pop("key")

        name = d.pop("name")

        tier = EntitlementPlanTier(d.pop("tier"))

        entitlement_plan = cls(
            key=key,
            name=name,
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

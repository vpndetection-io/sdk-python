from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AccountUsage")


@_attrs_define
class AccountUsage:
    """
    Attributes:
        requests (int): Requests counted in the current window. The same number the lookup
            API gates on, and it can lag by a few seconds.
        quota (int): What the plan includes. Zero on a plan that includes none.
        hard_limit (int | None): Where we stop serving. NULL means never, which is the normal state
            of an uncapped paid plan and is not the same as zero. Above the
            quota and below this, requests are served and billed as overage.
        window_start (datetime.datetime): When the current allowance period began.
        window_end (datetime.datetime): When the allowance next resets.
    """

    requests: int
    quota: int
    hard_limit: int | None
    window_start: datetime.datetime
    window_end: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        requests = self.requests

        quota = self.quota

        hard_limit: int | None
        hard_limit = self.hard_limit

        window_start = self.window_start.isoformat()

        window_end = self.window_end.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "requests": requests,
                "quota": quota,
                "hard_limit": hard_limit,
                "window_start": window_start,
                "window_end": window_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        requests = d.pop("requests")

        quota = d.pop("quota")

        def _parse_hard_limit(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        hard_limit = _parse_hard_limit(d.pop("hard_limit"))

        window_start = datetime.datetime.fromisoformat(d.pop("window_start"))

        window_end = datetime.datetime.fromisoformat(d.pop("window_end"))

        account_usage = cls(
            requests=requests,
            quota=quota,
            hard_limit=hard_limit,
            window_start=window_start,
            window_end=window_end,
        )

        account_usage.additional_properties = d
        return account_usage

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

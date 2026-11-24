from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BotDetail")


@_attrs_define
class BotDetail:
    """Bot IP's row: whose bot uses the address, the bots it serves or claimed to be, what they do, and how that is known.

    Attributes:
        provider (str | Unset): The bot operator's ID; for an address that is not verified, the operator its claim
            named. Empty where no operator is known.
        provider_name (str | Unset): That operator's name, empty where no operator is known.
        agents (list[str] | Unset): The bots the address serves, as their user agents name them (`Googlebot`, `GPTBot`);
            for an address that is not verified, the bots it claimed to be. One address can serve several, and `[]` means
            none is named.
        categories (list[str] | Unset): What those bots do: `search_engine`, `ai_training`, `ai_search`, `ai_assistant`,
            `ai_agent`, `seo`, `ads`, `preview`, `feed`, `monitoring`, `archiver`, `scanner`, `link_security`, `webhook` or
            `other`; `[]` where unknown.
        verified (bool | Unset): Whether the operator vouches for the address, so the bots in `agents` really are its.
        identity (str | Unset): `verified` (the operator vouches for the address), `declared` (it names itself a bot
            that cannot be verified), `spoofed` (it claimed a bot whose operator vouches for other addresses) or
            `undeclared` (it hides as a browser and behaves as automation).
        verified_by (str | Unset): How a verified address verified: `list` (the operator publishes it), `rdns` (its
            reverse DNS name ends in a suffix the operator documents and resolves back) or `owner` (the operator's own
            space, seen claiming its bot); empty when not verified.
        confidence (str | Unset): `high`, `medium` or `low`: how sure we are the address is what the row says.
        first_seen (datetime.date | Unset): The first day the address was seen as such.
        last_seen (datetime.date | Unset): The last day it was.
    """

    provider: str | Unset = UNSET
    provider_name: str | Unset = UNSET
    agents: list[str] | Unset = UNSET
    categories: list[str] | Unset = UNSET
    verified: bool | Unset = UNSET
    identity: str | Unset = UNSET
    verified_by: str | Unset = UNSET
    confidence: str | Unset = UNSET
    first_seen: datetime.date | Unset = UNSET
    last_seen: datetime.date | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        provider_name = self.provider_name

        agents: list[str] | Unset = UNSET
        if not isinstance(self.agents, Unset):
            agents = self.agents

        categories: list[str] | Unset = UNSET
        if not isinstance(self.categories, Unset):
            categories = self.categories

        verified = self.verified

        identity = self.identity

        verified_by = self.verified_by

        confidence = self.confidence

        first_seen: str | Unset = UNSET
        if not isinstance(self.first_seen, Unset):
            first_seen = self.first_seen.isoformat()

        last_seen: str | Unset = UNSET
        if not isinstance(self.last_seen, Unset):
            last_seen = self.last_seen.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if provider is not UNSET:
            field_dict["provider"] = provider
        if provider_name is not UNSET:
            field_dict["provider_name"] = provider_name
        if agents is not UNSET:
            field_dict["agents"] = agents
        if categories is not UNSET:
            field_dict["categories"] = categories
        if verified is not UNSET:
            field_dict["verified"] = verified
        if identity is not UNSET:
            field_dict["identity"] = identity
        if verified_by is not UNSET:
            field_dict["verified_by"] = verified_by
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if first_seen is not UNSET:
            field_dict["first_seen"] = first_seen
        if last_seen is not UNSET:
            field_dict["last_seen"] = last_seen

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        provider = d.pop("provider", UNSET)

        provider_name = d.pop("provider_name", UNSET)

        agents = cast(list[str], d.pop("agents", UNSET))

        categories = cast(list[str], d.pop("categories", UNSET))

        verified = d.pop("verified", UNSET)

        identity = d.pop("identity", UNSET)

        verified_by = d.pop("verified_by", UNSET)

        confidence = d.pop("confidence", UNSET)

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

        bot_detail = cls(
            provider=provider,
            provider_name=provider_name,
            agents=agents,
            categories=categories,
            verified=verified,
            identity=identity,
            verified_by=verified_by,
            confidence=confidence,
            first_seen=first_seen,
            last_seen=last_seen,
        )

        bot_detail.additional_properties = d
        return bot_detail

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

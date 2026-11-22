from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_agent_verdict_verdict import UserAgentVerdictVerdict

T = TypeVar("T", bound="UserAgentVerdict")


@_attrs_define
class UserAgentVerdict:
    """
    Attributes:
        agent (str): The agent the user agent names, such as `Googlebot` or `Chrome`; `Unknown` where it names none.
            Example: Googlebot.
        kind (str): `browser`, `inapp`, `automation`, `bot`, `ai-bot`, `http-client` or
            `unknown`: what kind of client the user agent says it is.
             Example: bot.
        verdict (UserAgentVerdictVerdict): `verified`: the agent's operator vouches for this address as it.
            `spoofed`: the operator of a bot that publishes its addresses, or
            whose registered space it uses, does not vouch for this one, or this
            address posed as the bot before. `unverifiable`: a bot no published
            list or registered space can confirm. `not_bot`: a browser, an app or
            a script.
             Example: verified.
    """

    agent: str
    kind: str
    verdict: UserAgentVerdictVerdict
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agent = self.agent

        kind = self.kind

        verdict = self.verdict.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agent": agent,
                "kind": kind,
                "verdict": verdict,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        agent = d.pop("agent")

        kind = d.pop("kind")

        verdict = UserAgentVerdictVerdict(d.pop("verdict"))

        user_agent_verdict = cls(
            agent=agent,
            kind=kind,
            verdict=verdict,
        )

        user_agent_verdict.additional_properties = d
        return user_agent_verdict

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

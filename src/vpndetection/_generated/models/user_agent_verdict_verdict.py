from enum import StrEnum


class UserAgentVerdictVerdict(StrEnum):
    NOT_BOT = "not_bot"
    SPOOFED = "spoofed"
    UNVERIFIABLE = "unverifiable"
    VERIFIED = "verified"

    def __str__(self) -> str:
        return str(self.value)

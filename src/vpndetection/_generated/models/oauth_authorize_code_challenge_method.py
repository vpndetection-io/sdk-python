from enum import StrEnum


class OauthAuthorizeCodeChallengeMethod(StrEnum):
    S256 = "S256"

    def __str__(self) -> str:
        return str(self.value)

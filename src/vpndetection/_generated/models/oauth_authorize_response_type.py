from enum import StrEnum


class OauthAuthorizeResponseType(StrEnum):
    CODE = "code"

    def __str__(self) -> str:
        return str(self.value)

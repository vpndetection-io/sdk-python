from enum import StrEnum


class Standing(StrEnum):
    EXPIRED = "expired"
    LICENSED = "licensed"
    UNLICENSED = "unlicensed"

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, value: object) -> "Standing | None":
        # A value the API added after this release, handed back as served.
        if not isinstance(value, str):
            return None
        member = str.__new__(cls, value)
        member._name_ = value
        member._value_ = value
        return member

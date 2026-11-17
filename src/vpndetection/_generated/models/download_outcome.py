from enum import StrEnum


class DownloadOutcome(StrEnum):
    DENIED = "denied"
    EXPIRED = "expired"
    OK = "ok"
    UNAUTHORIZED = "unauthorized"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, value: object) -> "DownloadOutcome | None":
        # A value the API added after this release, handed back as served.
        if not isinstance(value, str):
            return None
        member = str.__new__(cls, value)
        member._name_ = value
        member._value_ = value
        return member

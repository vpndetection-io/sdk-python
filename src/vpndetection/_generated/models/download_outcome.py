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

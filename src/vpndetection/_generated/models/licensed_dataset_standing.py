from enum import StrEnum


class LicensedDatasetStanding(StrEnum):
    EXPIRED = "expired"
    LICENSED = "licensed"
    UNLICENSED = "unlicensed"

    def __str__(self) -> str:
        return str(self.value)

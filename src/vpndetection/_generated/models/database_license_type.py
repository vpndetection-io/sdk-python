from enum import StrEnum


class DatabaseLicenseType(StrEnum):
    EVALUATION = "evaluation"
    REDISTRIBUTE = "redistribute"
    STANDARD = "standard"

    def __str__(self) -> str:
        return str(self.value)

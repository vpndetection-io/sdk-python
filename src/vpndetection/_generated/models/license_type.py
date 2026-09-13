from enum import StrEnum


class LicenseType(StrEnum):
    EVALUATION = "evaluation"
    REDISTRIBUTE = "redistribute"
    STANDARD = "standard"

    def __str__(self) -> str:
        return str(self.value)

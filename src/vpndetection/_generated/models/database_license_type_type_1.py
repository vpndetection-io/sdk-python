from enum import StrEnum


class DatabaseLicenseTypeType1(StrEnum):
    EVALUATION = "evaluation"
    REDISTRIBUTE = "redistribute"
    STANDARD = "standard"

    def __str__(self) -> str:
        return str(self.value)

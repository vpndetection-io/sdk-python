from enum import StrEnum


class LicensedDatasetRedistribution(StrEnum):
    EVALUATION = "evaluation"
    INTERNAL = "internal"
    REDISTRIBUTE = "redistribute"

    def __str__(self) -> str:
        return str(self.value)

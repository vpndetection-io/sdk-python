from enum import StrEnum


class EntitlementPlanTier(StrEnum):
    FREE = "free"
    MAX = "max"
    SCALE = "scale"
    STARTER = "starter"

    def __str__(self) -> str:
        return str(self.value)

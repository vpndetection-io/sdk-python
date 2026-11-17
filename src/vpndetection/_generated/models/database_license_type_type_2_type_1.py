from enum import StrEnum


class DatabaseLicenseTypeType2Type1(StrEnum):
    EVALUATION = "evaluation"
    REDISTRIBUTE = "redistribute"
    STANDARD = "standard"

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, value: object) -> "DatabaseLicenseTypeType2Type1 | None":
        # A value the API added after this release, handed back as served.
        if not isinstance(value, str):
            return None
        member = str.__new__(cls, value)
        member._name_ = value
        member._value_ = value
        return member

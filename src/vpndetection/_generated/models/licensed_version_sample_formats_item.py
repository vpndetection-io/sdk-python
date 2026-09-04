from enum import StrEnum


class LicensedVersionSampleFormatsItem(StrEnum):
    CSVGZ = "csvgz"
    MMDB = "mmdb"

    def __str__(self) -> str:
        return str(self.value)

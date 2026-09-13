from enum import StrEnum


class DatabaseVersionSampleFormatsItem(StrEnum):
    CSVGZ = "csvgz"
    MMDB = "mmdb"

    def __str__(self) -> str:
        return str(self.value)

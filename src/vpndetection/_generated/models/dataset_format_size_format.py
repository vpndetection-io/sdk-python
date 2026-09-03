from enum import StrEnum


class DatasetFormatSizeFormat(StrEnum):
    CSVGZ = "csvgz"
    MMDB = "mmdb"

    def __str__(self) -> str:
        return str(self.value)

from enum import StrEnum


class DownloadDatabaseFormat(StrEnum):
    CSVGZ = "csvgz"
    MMDB = "mmdb"

    def __str__(self) -> str:
        return str(self.value)

"""The official Python client library for the VPNDetection API.

    from vpndetection import VPNDetection

    with VPNDetection() as client:
        print(client.lookup("45.83.91.1").is_vpn)

No API key is needed to start. See https://vpndetection.io for the API, and the README
for batching, caching and the licensed dataset downloads.
"""

from ._core import DEFAULT_BASE_URL
from ._generated.models.dataset_format_size import DatasetFormatSize
from ._generated.models.dataset_metadata import DatasetMetadata
from ._generated.models.dataset_metadata_column import DatasetMetadataColumn
from ._generated.models.download import Download
from ._generated.models.licensed_dataset import LicensedDataset
from .aio import AsyncDatabaseApi, AsyncVPNDetection
from .bogon import is_bogon
from .client import DatabaseApi, VPNDetection
from .errors import ErrorKind, VPNDetectionError
from .models import ClassDetail, Flag, Format, ProxyDetail, Result, VpnDetail

__version__ = "1.0.0"

__all__ = [
    "DEFAULT_BASE_URL",
    "AsyncDatabaseApi",
    "AsyncVPNDetection",
    "ClassDetail",
    "DatabaseApi",
    "DatasetFormatSize",
    "DatasetMetadata",
    "DatasetMetadataColumn",
    "Download",
    "ErrorKind",
    "Flag",
    "Format",
    "LicensedDataset",
    "ProxyDetail",
    "Result",
    "VPNDetection",
    "VPNDetectionError",
    "VpnDetail",
    "__version__",
    "is_bogon",
]

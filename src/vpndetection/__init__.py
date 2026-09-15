"""The official Python client library for the VPNDetection API.

    from vpndetection import VPNDetection

    with VPNDetection() as client:
        print(client.lookup("45.83.91.1").is_vpn)

No API key is needed to start. See https://vpndetection.io for the API, and the README
for batching, caching and the licensed dataset downloads.
"""

from ._core import DEFAULT_BASE_URL
from ._generated.models.entitlement_apikey import EntitlementApikey
from ._generated.models.entitlement import Entitlement
from ._generated.models.entitlement_plan import EntitlementPlan
from ._generated.models.entitlement_plan_tier import EntitlementPlanTier
from ._generated.models.entitlement_usage import EntitlementUsage
from ._generated.models.database import Database
from ._generated.models.database_format_size import DatabaseFormatSize
from ._generated.models.database_metadata import DatabaseMetadata
from ._generated.models.database_metadata_column import DatabaseMetadataColumn
from ._generated.models.database_version import DatabaseVersion
from ._generated.models.download import Download
from .aio import AsyncDatabaseApi, AsyncVPNDetection
from .bogon import is_bogon
from .client import DatabaseApi, VPNDetection
from .errors import ErrorKind, VPNDetectionError
from .models import ClassDetail, Flag, Format, ProxyDetail, Result, VpnDetail

__version__ = "4.0.1"

__all__ = [
    "DEFAULT_BASE_URL",
    "EntitlementApikey",
    "Entitlement",
    "EntitlementPlan",
    "EntitlementPlanTier",
    "EntitlementUsage",
    "AsyncDatabaseApi",
    "AsyncVPNDetection",
    "ClassDetail",
    "Database",
    "DatabaseApi",
    "DatabaseFormatSize",
    "DatabaseMetadata",
    "DatabaseMetadataColumn",
    "DatabaseVersion",
    "Download",
    "ErrorKind",
    "Flag",
    "Format",
    "ProxyDetail",
    "Result",
    "VPNDetection",
    "VPNDetectionError",
    "VpnDetail",
    "__version__",
    "is_bogon",
]

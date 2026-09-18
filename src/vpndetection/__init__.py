"""The official Python client library for the VPNDetection API.

    from vpndetection import VPNDetection

    with VPNDetection() as client:
        print(client.lookup("45.83.91.1").is_vpn)

No API key is needed to start. See https://vpndetection.io for the API, and the README
for batching, caching and the licensed dataset downloads.
"""

from ._core import DEFAULT_BASE_URL
from ._generated.models.database import Database
from ._generated.models.database_format_size import DatabaseFormatSize
from ._generated.models.database_metadata import DatabaseMetadata
from ._generated.models.database_metadata_column import DatabaseMetadataColumn
from ._generated.models.database_version import DatabaseVersion
from ._generated.models.download import Download
from ._generated.models.entitlement import Entitlement
from ._generated.models.entitlement_apikey import EntitlementApikey
from ._generated.models.entitlement_plan import EntitlementPlan
from ._generated.models.entitlement_plan_tier import EntitlementPlanTier
from ._generated.models.entitlement_usage import EntitlementUsage
from .aio import AsyncDatabaseApi, AsyncOauthApi, AsyncVPNDetection
from .bogon import is_bogon
from .client import DatabaseApi, OauthApi, VPNDetection
from .errors import (
    ErrorKind,
    OauthAccessDeniedError,
    OauthError,
    OauthExpiredTokenError,
    VPNDetectionError,
)
from .models import (
    DATABASE_FORMATS,
    LICENSE_TYPES,
    STANDINGS,
    ClassDetail,
    DeviceAuthorization,
    Flag,
    Format,
    OauthMetadata,
    ProxyDetail,
    Result,
    TokenResponse,
    VpnDetail,
)

__version__ = "5.4.0"

__all__ = [
    "DATABASE_FORMATS",
    "DEFAULT_BASE_URL",
    "LICENSE_TYPES",
    "STANDINGS",
    "AsyncDatabaseApi",
    "AsyncOauthApi",
    "AsyncVPNDetection",
    "ClassDetail",
    "Database",
    "DatabaseApi",
    "DatabaseFormatSize",
    "DatabaseMetadata",
    "DatabaseMetadataColumn",
    "DatabaseVersion",
    "DeviceAuthorization",
    "Download",
    "Entitlement",
    "EntitlementApikey",
    "EntitlementPlan",
    "EntitlementPlanTier",
    "EntitlementUsage",
    "ErrorKind",
    "Flag",
    "Format",
    "OauthAccessDeniedError",
    "OauthApi",
    "OauthError",
    "OauthExpiredTokenError",
    "OauthMetadata",
    "ProxyDetail",
    "Result",
    "TokenResponse",
    "VPNDetection",
    "VPNDetectionError",
    "VpnDetail",
    "__version__",
    "is_bogon",
]

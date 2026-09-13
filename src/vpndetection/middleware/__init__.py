"""The framework-agnostic half of a web middleware.

What the framework adapters - vpndetection-django, vpndetection-flask,
vpndetection-fastapi - are built on. Using it directly is how you support a framework
none of them cover.
"""

from .condition import (
    BlockCondition,
    Conditions,
    constraint_count,
    matches,
    missing_members,
    validate,
)
from .core import (
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncCore,
    Core,
    IpSelector,
    Lookup,
    MissingFieldAction,
    Options,
    RequestView,
    Selectors,
    bind_selectors,
)

__all__ = [
    "DEFAULT_RETRIES",
    "DEFAULT_TIMEOUT",
    "AsyncCore",
    "BlockCondition",
    "Conditions",
    "Core",
    "IpSelector",
    "Lookup",
    "MissingFieldAction",
    "Options",
    "RequestView",
    "Selectors",
    "bind_selectors",
    "constraint_count",
    "matches",
    "missing_members",
    "validate",
]

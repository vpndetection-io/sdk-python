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
    MAX_AGENTS_PER_ADDRESS,
    AsyncCore,
    Core,
    Guard,
    IpSelector,
    Lookup,
    MissingFieldAction,
    Options,
    RequestView,
    Selectors,
    UserAgentSelector,
    bind_selectors,
    names_crawler,
    verified,
)

__all__ = [
    "DEFAULT_RETRIES",
    "DEFAULT_TIMEOUT",
    "MAX_AGENTS_PER_ADDRESS",
    "AsyncCore",
    "BlockCondition",
    "Conditions",
    "Core",
    "Guard",
    "IpSelector",
    "Lookup",
    "MissingFieldAction",
    "Options",
    "RequestView",
    "Selectors",
    "UserAgentSelector",
    "bind_selectors",
    "constraint_count",
    "matches",
    "missing_members",
    "names_crawler",
    "validate",
    "verified",
]

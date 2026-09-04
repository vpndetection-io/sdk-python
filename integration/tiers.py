"""Which plan tiers this run can observe, and the secret each one needs.

Imported by `scripts/run.py` as well as by the tests, so it must not touch the package
under test: the runner reads the tier table BEFORE pip has installed anything.

A tier is observable only when its secret holds something non-empty. Actions interpolates
a secret that does not exist to an EMPTY STRING rather than leaving the variable unset,
and a client built with an empty key sends no credential at all, so an empty key runs as
a second unauthenticated client and every comparison against it is vacuously true.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Rung:
    """One plan tier, and how a run reaches it.

    `widens` is what the rung promises against whichever observable rung sits below it: a
    paid tier serves strictly more than the tier under it, while a free key and no key at
    all are the same entitlement reached two ways.

    Field COUNTS are deliberately absent. Pinning "starter answers seven fields" turns a
    pricing change into a red SDK build; the relation between the tiers is what the
    client actually has to keep.
    """

    tier: str
    secret: str | None
    widens: bool

    def key(self) -> str:
        if self.secret is None:
            return ""
        return os.environ.get(self.secret, "").strip()

    def skip_reason(self) -> str | None:
        """A reason to skip, or None when this rung can be exercised."""
        if self.secret is None or self.key() != "":
            return None
        return f"{self.secret} is not set, so the {self.tier} tier cannot be exercised"


# Ascending, one rung per plan tier.
RUNGS = [
    Rung("unauth", None, widens=False),
    Rung("free", "VPNDETECTION_STAGING_KEY_FREE", widens=False),
    Rung("starter", "VPNDETECTION_STAGING_KEY_STARTER", widens=True),
    Rung("scale", "VPNDETECTION_STAGING_KEY_SCALE", widens=True),
    Rung("max", "VPNDETECTION_STAGING_KEY_MAX", widens=True),
]

UNAUTH = RUNGS[0]
# The tier holding the dataset licenses: `db.download` is a scope the other three keys do
# not carry.
MAX = RUNGS[-1]


def observable() -> list[Rung]:
    return [rung for rung in RUNGS if rung.skip_reason() is None]


def ladder_skip() -> str | None:
    """A reason the ladder cannot be compared, or None.

    It needs two rungs to say anything. The unauthenticated one is always there, so this
    only fires when no tier secret at all is configured.
    """
    if len(observable()) > 1:
        return None
    return "no tier secret is set, so there is no ladder to compare"

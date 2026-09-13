"""Deciding whether an answer is worth blocking.

The condition is written in the shape of a `Result` and keyed by the same names the
API uses, so what you write here reads like what you get back.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "BlockCondition",
    "Conditions",
    "constraint_count",
    "matches",
    "missing_members",
    "validate",
]

#: What makes a request worth blocking. Only the members you name are considered, and
#: they must all hold.
#:
#: A value may be a scalar (equality, strings without regard to case), a list meaning
#: any-of, a dict of ``gte``/``gt``/``lte``/``lt`` bounding a number, or a nested
#: condition. A member set to ``False`` or ``None`` is ignored entirely - a condition
#: states the positive signals you act on, so there is no way to write "block when this
#: is false", which would otherwise read as blocking everybody::
#:
#:     {"is_vpn": True}
#:     {"is_vpn": True, "vpn": {"provider": "nordvpn"}}
#:     {"is_resproxy": True, "resproxy": {"hits": {"gte": 5}}}
#:     {"vpn": {"confidence": ["high", "medium"]}}
BlockCondition = dict[str, Any]

#: One condition, or a list of them meaning any one blocking is enough.
Conditions = BlockCondition | list[BlockCondition]

_BOUND_KEYS = frozenset({"gte", "gt", "lte", "lt"})


def matches(condition: Conditions, result: Any) -> bool:
    """Whether an answer satisfies the condition, and should therefore be blocked."""
    for one in _as_list(condition):
        if _matches_object(one, result):
            return True
    return False


def missing_members(condition: Conditions, result: Any) -> list[str]:
    """The top-level members a condition names that this answer did not carry.

    A field your plan does not include is absent rather than false, so a condition
    naming one can never match and the block would silently never fire. Gating is per
    top-level member, which is why only the first path segment is checked: a detail
    object present but empty is a real answer meaning the flag is false, not a plan gap.

    A locally answered bogon needs no special case: it is synthesized in the widest
    shape, so every member is present and nothing reads as missing.
    """
    missing: list[str] = []
    for one in _as_list(condition):
        for member, want in one.items():
            if constraint_count(want) == 0 or member in missing:
                continue
            if getattr(result, member, None) is None:
                missing.append(member)
    return missing


def validate(condition: Conditions | None) -> None:
    """Refuse a condition that constrains nothing.

    Ignoring ``False`` means ``{"is_vpn": False}`` and ``{}`` have no terms left to
    satisfy, so they would match every answer and block all traffic. Nobody writes that
    on purpose, and failing when the middleware is built beats discovering it in
    production.
    """
    if condition is None:
        return
    for one in _as_list(condition):
        if constraint_count(one) == 0:
            raise ValueError(
                f"vpndetection: block condition {one!r} constrains nothing, which would "
                "block every request; a member set to False or None is ignored, so state "
                "the positive signals you act on"
            )


def constraint_count(condition: Any) -> int:
    """How many leaf constraints a condition actually carries."""
    if condition is None or condition is False:
        return 0
    if isinstance(condition, dict):
        if _is_bound(condition):
            return 1
        return sum(constraint_count(value) for value in condition.values())
    if isinstance(condition, (list, tuple, set, frozenset)):
        return sum(constraint_count(entry) for entry in condition)
    return 1


def _as_list(condition: Conditions) -> list[BlockCondition]:
    if isinstance(condition, list):
        return condition
    return [condition]


def _matches_object(condition: BlockCondition, value: Any) -> bool:
    for member, want in condition.items():
        if constraint_count(want) == 0:
            continue
        if not _matches_value(want, getattr(value, member, None)):
            return False
    return True


def _matches_value(want: Any, got: Any) -> bool:
    """Whether one value satisfies one want.

    An ABSENT member arrives here as ``None``, which is exactly what "not in your plan"
    looks like. Every branch below must therefore reject it, which is what makes an
    unserved member fail a match rather than pass it. A new branch that does not would
    silently let a member nobody was served block a request.
    """
    if isinstance(want, (list, tuple, set, frozenset)):
        return any(_matches_value(entry, got) for entry in want)
    if isinstance(want, dict):
        if _is_bound(want):
            return _matches_bound(want, got)
        return _matches_object(want, got)
    if isinstance(want, str) and isinstance(got, str):
        # Providers are lowercase slugs on the wire and a caller should not have to
        # know that, so a string compares without case.
        return want.casefold() == got.casefold()
    if isinstance(want, bool) or isinstance(got, bool):
        return want is got
    return bool(want == got)


def _matches_bound(bound: dict[str, Any], got: Any) -> bool:
    if isinstance(got, bool) or not isinstance(got, (int, float)):
        return False
    if "gte" in bound and got < bound["gte"]:
        return False
    if "gt" in bound and got <= bound["gt"]:
        return False
    if "lte" in bound and got > bound["lte"]:
        return False
    return not ("lt" in bound and got >= bound["lt"])


def _is_bound(value: dict[str, Any]) -> bool:
    return len(value) > 0 and _BOUND_KEYS.issuperset(value)

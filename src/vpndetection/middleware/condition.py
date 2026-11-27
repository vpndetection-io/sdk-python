"""Deciding whether an answer is worth blocking.

The condition is written in the shape of a `Result` and keyed by the same names the
API uses, so what you write here reads like what you get back.
"""

from __future__ import annotations

import dataclasses
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
    raw = getattr(result, "raw", None)
    for one in _as_list(condition):
        if _matches_object(one, result, raw):
            return True
    return False


def missing_members(condition: Conditions, result: Any) -> list[str]:
    """The members a condition names that this answer did not carry: a top-level member,
    or a paid one inside an object every plan gets, by its path (``asn.type``).

    A field your plan does not include is absent rather than false, so a condition
    naming one can never match and the block would silently never fire. Gating is per
    top-level member, so a detail object present but empty is a real answer meaning the
    flag is false, not a plan gap. Inside an object that is present, only a member the
    type holds at its empty value (``asn.type``) is reported, and only when the answer as
    served lacked it: the empty value is never read as one the answer carried.

    A locally answered bogon needs no special case: it is synthesized in the widest
    shape, so every member is present and nothing reads as missing.
    """
    missing: list[str] = []
    raw = getattr(result, "raw", None)
    for one in _as_list(condition):
        _collect_missing(one, result, raw, "", missing)
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


def _collect_missing(
    condition: BlockCondition, value: Any, raw: Any, prefix: str, missing: list[str]
) -> None:
    for member, want in condition.items():
        if constraint_count(want) == 0:
            continue
        path = f"{prefix}{member}"
        got = getattr(value, member, None)
        if _left_out(value, member, raw) or (not prefix and got is None):
            if path not in missing:
                missing.append(path)
            continue
        if isinstance(want, dict) and not _is_bound(want) and _is_record(got):
            _collect_missing(want, got, _wire_of(raw, member), f"{path}.", missing)


def _is_record(value: Any) -> bool:
    return dataclasses.is_dataclass(value) and not isinstance(value, type)


def _wire_of(raw: Any, member: str) -> Any:
    """The part of the served answer a member was read from."""
    return raw.get(member) if isinstance(raw, dict) else None


def _left_out(value: Any, member: str, raw: Any) -> bool:
    """Whether the served answer lacked a member the type holds at its empty value
    (``asn.type``). The type reads the empty string either way, so only the answer as
    served says; one with none (a bogon's, or a type built by hand) reads as it was built,
    and a value that is not the empty one is a value whatever the answer carried."""
    fields = getattr(value, "__dataclass_fields__", {})
    held = fields.get(member)
    if held is None or not held.metadata.get("held") or not isinstance(raw, dict) or not raw:
        return False
    return member not in raw and getattr(value, member, None) == held.default


def _matches_object(condition: BlockCondition, value: Any, raw: Any = None) -> bool:
    for member, want in condition.items():
        if constraint_count(want) == 0:
            continue
        got = None if _left_out(value, member, raw) else getattr(value, member, None)
        if not _matches_value(want, got, _wire_of(raw, member)):
            return False
    return True


def _matches_value(want: Any, got: Any, raw: Any = None) -> bool:
    """Whether one value satisfies one want.

    An ABSENT member arrives here as ``None``, which is exactly what "not in your plan"
    looks like. Every branch below must therefore reject it, which is what makes an
    unserved member fail a match rather than pass it. A new branch that does not would
    silently let a member nobody was served block a request.

    A member the answer holds as a list (``pubproxy.protocols``, the ``web`` rows)
    matches when any one element does, so an object term is a partial match on a
    single element, never spread across several.
    """
    if isinstance(got, (list, tuple)):
        return any(_matches_value(want, element) for element in got)
    if isinstance(want, (list, tuple, set, frozenset)):
        return any(_matches_value(entry, got) for entry in want)
    if isinstance(want, dict):
        if _is_bound(want):
            return _matches_bound(want, got)
        return _matches_object(want, got, raw)
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

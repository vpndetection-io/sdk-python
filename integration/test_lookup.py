"""The published package looking addresses up against the staging API.

Nothing here pins a field COUNT. The tiers are asserted as a RELATION, each one serving a
superset of the tier below it, so a pricing change stays a pricing change instead of
arriving as a red SDK build. What a served answer must satisfy on every tier: `ip` and
`is_vpn` always; a present flag is a real boolean; a field a higher tier serves is ABSENT
on a lower one rather than false; a populated detail object carries its documented keys;
an empty one means its flag is false.
"""

from __future__ import annotations

import dataclasses

import httpx
import pytest
import staging
import tiers
from staging import PROBE, STAGING, answer_for, assert_served_by_tier, modelled

from vpndetection import VPNDetection, is_bogon


def test_an_unauthenticated_lookup_answers_ip_and_is_vpn() -> None:
    answer = answer_for(tiers.UNAUTH)

    assert answer.raw["ip"] == PROBE
    assert isinstance(answer.raw["is_vpn"], bool)
    assert_served_by_tier(answer)
    print(f"==> testing against {STAGING}")


@pytest.mark.parametrize(
    "rung", [rung for rung in tiers.RUNGS if rung.secret], ids=lambda r: r.tier
)
def test_a_key_reaches_the_wire_and_its_answer_keeps_its_shape(rung: tiers.Rung) -> None:
    reason = rung.skip_reason()
    if reason:
        pytest.skip(reason)

    assert_served_by_tier(answer_for(rung))


def test_each_tier_serves_a_superset_of_the_tier_below() -> None:
    reason = tiers.ladder_skip()
    if reason:
        pytest.skip(reason)

    below = None
    for rung in tiers.observable():
        answer = answer_for(rung)
        print(f"==> {rung.tier}: {len(answer.raw)} fields")
        if below is None:
            below = answer
            continue
        for field in below.raw:
            assert field in answer.raw, f"{rung.tier} drops {field}, which {below.rung.tier} serves"
        # Without this a run in which every key resolved to the same plan would pass:
        # identical sets satisfy containment in both directions.
        if rung.widens:
            assert len(answer.raw) > len(below.raw), (
                f"{rung.tier} answers {len(answer.raw)} field(s) and {below.rung.tier} "
                f"answers {len(below.raw)}, so it is no wider"
            )
        below = answer


def test_a_field_a_higher_tier_serves_is_absent_on_a_lower_one_never_false() -> None:
    reason = tiers.ladder_skip()
    if reason:
        pytest.skip(reason)

    answers = [answer_for(rung) for rung in tiers.observable()]

    # The positive half: a field the wire carried must have reached the result, which is
    # what makes a served `false` survive.
    for answer in answers:
        for field in sorted(answer.raw):
            value, models_it = modelled(answer.result, field)
            if models_it:
                assert value is not None, (
                    f"{answer.rung.tier} serves {field} and the client dropped it"
                )

    for index, lower in enumerate(answers):
        higher = {field for above in answers[index + 1 :] for field in above.raw}
        for field in sorted(higher - set(lower.raw)):
            value, models_it = modelled(lower.result, field)
            if not models_it:
                continue
            assert value is None, (
                f"{field} is not in the {lower.rung.tier} plan, so the result must not "
                f"read as {value!r}"
            )


def test_a_bogon_is_answered_without_touching_the_network() -> None:
    with VPNDetection(base_url=STAGING, transport=Refusing()) as client:
        result = client.lookup("10.0.0.1")

    assert result.is_bogon is True, "a private address must be answered locally"
    assert result.is_vpn is False, "a private address cannot be VPN infrastructure"
    assert is_bogon("10.0.0.1"), "the standalone function must agree with the client"
    # Computed rather than served, so it carries every field whatever the plan.
    for name in staging.MEMBERS:
        assert getattr(result, f"is_{name}") is False, f"is_{name} must be present and false"
        detail = getattr(result, name)
        assert detail is not None, f"{name} must be present and empty on a bogon"
        assert all(value is None for value in dataclasses.asdict(detail).values()), (
            f"{name} must be present and EMPTY on a bogon, got {detail}"
        )


def test_a_batch_collapses_duplicates_and_keeps_bogons_off_the_wire() -> None:
    client, recorder = staging.client_for(tiers.UNAUTH)
    try:
        got = client.lookup_batch([PROBE, "8.8.8.8", PROBE, "10.0.0.1", "8.8.8.8"])
    finally:
        client.close()

    assert sorted(got) == sorted([PROBE, "8.8.8.8", "10.0.0.1"])
    # Distinct paths rather than a call count, so a retry against a wobbling staging cannot
    # read as a failure to deduplicate.
    assert sorted({fact.path for fact in recorder.facts}) == sorted([f"/{PROBE}", "/8.8.8.8"])
    bogon = got["10.0.0.1"]
    assert not isinstance(bogon, Exception) and bogon.is_bogon, "10.0.0.1 reached the network"
    for ip in (PROBE, "8.8.8.8"):
        assert not isinstance(got[ip], Exception), f"{ip} failed: {got[ip]}"


class Refusing(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        raise AssertionError(f"the bogon path reached the network at {request.url}")

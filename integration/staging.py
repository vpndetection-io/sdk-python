"""The staging fixtures the test files share: the gate that keeps this suite honest, one
client per tier, one lookup per tier, and the shape rules that hold whatever the plan."""

from __future__ import annotations

import dataclasses
import importlib.metadata
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
from tiers import Rung

from vpndetection import AsyncVPNDetection, Result, VPNDetection

STAGING = "https://api-staging.vpndetection.io"

# A stable VPN address, and the one the README teaches.
PROBE = "45.83.91.1"

PACKAGE = "vpndetection"


@dataclass(frozen=True)
class Detail:
    """What a POPULATED detail object carries.

    `required` holds on every tier; `optional` is the max-only remainder, which is absent
    rather than empty on a lower plan.
    """

    required: tuple[str, ...]
    optional: tuple[str, ...] = ()


CLASS_KEYS = ("provider", "confidence", "last_seen")
PROXY_KEYS = ("provider", "first_seen", "last_seen", "hits", "hits_days_pct", "providers_num")

# One entry per dataset the API answers about.
MEMBERS = {
    "vpn": Detail(required=("provider", "last_seen"), optional=("confidence", "method")),
    "hosting": Detail(required=CLASS_KEYS),
    "relay": Detail(required=CLASS_KEYS),
    "tor": Detail(required=CLASS_KEYS),
    "cdn": Detail(required=CLASS_KEYS),
    "resproxy": Detail(required=PROXY_KEYS),
    "dcproxy": Detail(required=PROXY_KEYS),
    "mobproxy": Detail(required=PROXY_KEYS),
}

# Everything on a Result that came off the wire. The other two are the library's own: one
# is computed rather than served, the other is the wire itself.
WIRE_FIELDS = {field.name for field in dataclasses.fields(Result)} - {"is_bogon", "raw"}


def assert_published_artifact() -> None:
    """Refuse to run against the working tree.

    This suite exists to test the artifact a stranger installs, and running it against
    local source is the one failure that is completely silent: every test passes, against
    code no consumer has. Two ways that happens, and each is ruled out here.

    The import resolves inside this repository's own `src`, which is what a stray
    PYTHONPATH or an editable install gives you. Note the test is `src` rather than the
    repository, because the virtualenv the runner builds lives under `integration/` and is
    exactly where a legitimate install lands.

    Or the distribution came from a path rather than a registry, which is a locally built
    wheel passed off as a release. Nothing about the installed files would show that; pip
    records it in `direct_url.json`, which a registry install does not write at all.
    """
    module = __import__(PACKAGE)
    where = Path(module.__file__ or "").resolve()
    source = Path(__file__).resolve().parent.parent / "src"
    if source in where.parents:
        pytest.exit(f"{PACKAGE} imports from {where}, which is this repository's own source", 1)

    direct = importlib.metadata.distribution(PACKAGE).read_text("direct_url.json")
    if direct is None:
        return
    url = json.loads(direct).get("url", "")
    if not url.startswith("https://"):
        pytest.exit(f"{PACKAGE} was installed from {url}, which is not a registry", 1)


@dataclass(frozen=True)
class Fact:
    """What a test is allowed to remember about a request it made.

    Only derived facts leave here. An assertion that fails prints its operands, so holding
    on to the request itself is how a key ends up in a public CI log: whether the key was
    carried is a boolean, and the caller never sees the key.
    """

    origin: str
    path: str
    carried_key: bool


class Recorder(httpx.BaseTransport):
    """The real transport, remembering what it was asked for.

    One instance serves both the API client and the credential-free one the download path
    uses, so a single record holds the request that must carry the key and the request
    that must not.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        self.facts: list[Fact] = []
        self._inner = httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.facts.append(fact_for(request, self.key))
        return self._inner.handle_request(request)

    def close(self) -> None:
        self._inner.close()

    def carried_key(self) -> bool:
        return any(fact.carried_key for fact in self.facts)


class AsyncRecorder(httpx.AsyncBaseTransport):
    """`Recorder`, for the asyncio client."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.facts: list[Fact] = []
        self._inner = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.facts.append(fact_for(request, self.key))
        return await self._inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self._inner.aclose()

    def carried_key(self) -> bool:
        return any(fact.carried_key for fact in self.facts)


def fact_for(request: httpx.Request, key: str) -> Fact:
    carried = key != "" and (
        key in request.url.query.decode() or any(key in value for value in request.headers.values())
    )
    return Fact(
        origin=f"{request.url.scheme}://{request.url.netloc.decode()}",
        path=request.url.path,
        carried_key=carried,
    )


def client_for(rung: Rung) -> tuple[VPNDetection, Recorder]:
    recorder = Recorder(rung.key())
    # An empty key must arrive as no key: an `Authorization: Bearer ` with nothing after
    # it is a 401, not an unauthenticated request.
    client = VPNDetection(rung.key() or None, base_url=STAGING, transport=recorder)
    return client, recorder


def async_client_for(rung: Rung) -> tuple[AsyncVPNDetection, AsyncRecorder]:
    recorder = AsyncRecorder(rung.key())
    client = AsyncVPNDetection(rung.key() or None, base_url=STAGING, transport=recorder)
    return client, recorder


@dataclass(frozen=True)
class Answer:
    rung: Rung
    result: Result
    carried_key: bool

    @property
    def raw(self) -> dict[str, Any]:
        """What the wire carried, which is the plan itself: presence is the entitlement."""
        return self.result.raw


_answers: dict[str, Answer] = {}


def answer_for(rung: Rung) -> Answer:
    """One lookup per tier for the whole run.

    The client caches, so a second reader of the same tier would cost no request either,
    but the answer also carries whether the key reached the wire, which the client does
    not keep.
    """
    if rung.tier not in _answers:
        client, recorder = client_for(rung)
        try:
            result = client.lookup(PROBE)
        finally:
            client.close()
        answer = Answer(rung=rung, result=result, carried_key=recorder.carried_key())
        # Checked here rather than in one test, so no comparison anywhere can be made
        # against a tier that silently ran unauthenticated: an empty or unsent key answers
        # the free shape, which satisfies every containment check vacuously.
        if rung.secret is not None and not answer.carried_key:
            pytest.fail(f"{rung.tier}: the key never reached the wire")
        _answers[rung.tier] = answer
    return _answers[rung.tier]


def assert_served_by_tier(answer: Answer) -> None:
    tier = answer.rung.tier
    assert answer.result.ip == PROBE, f"{tier}: answered about {answer.result.ip}, want {PROBE}"
    assert answer.result.is_bogon is False, f"{tier}: a served answer is not a local one"
    assert_shape(tier, answer.result)


def assert_shape(tier: str, result: Result) -> None:
    """Holds on every plan: presence is the plan, the value is the answer.

    Read off `raw`, which is the wire, then cross-checked against the typed field. That
    pairing is the positive half of the absent-versus-false contract: a field the plan
    DOES include must survive the mapping, `false` and all.
    """
    raw = result.raw
    assert isinstance(raw.get("ip"), str), f"{tier}: ip is {raw.get('ip')!r}, want a string"
    assert isinstance(raw.get("is_vpn"), bool), (
        f"{tier}: is_vpn is {raw.get('is_vpn')!r}, and it is on every plan"
    )
    assert result.is_vpn is raw["is_vpn"], f"{tier}: is_vpn did not survive the mapping"

    for name, spec in MEMBERS.items():
        flag = f"is_{name}"
        if flag in raw:
            assert isinstance(raw[flag], bool), (
                f"{tier}: {flag} is present, so it must be a real boolean, not {raw[flag]!r}"
            )
            assert getattr(result, flag) is raw[flag], f"{tier}: {flag} did not survive the mapping"
        if name not in raw:
            continue
        # A detail object without its flag would leave a caller reading the object to find
        # out whether the address is flagged at all.
        assert flag in raw, f"{tier}: {name} is served without {flag}"
        assert_detail(tier, name, spec, raw[name], raw[flag])


def assert_detail(tier: str, name: str, spec: Detail, detail: Any, flag: Any) -> None:
    assert isinstance(detail, dict), (
        f"{tier}: {name} must be an object when present, got {detail!r}"
    )
    if not detail:
        assert flag is False, f"{tier}: {name} is empty, so is_{name} must be false, not {flag!r}"
        return
    for key in spec.required:
        assert key in detail, f"{tier}: {name} is populated but carries no {key}"
    for key in detail:
        assert key in spec.required or key in spec.optional, (
            f"{tier}: {name}.{key} is not a documented key of this detail object"
        )


def modelled(result: Result, wire: str) -> tuple[Any, bool]:
    """What the client holds for a WIRE field name, and whether it models it at all.

    Asked by the name the API serves rather than by whatever the generator called it. A
    field the client does not model is the API moving ahead of the pinned spec, not a
    dropped one.
    """
    if wire not in WIRE_FIELDS:
        return None, False
    return getattr(result, wire), True


def notice(message: str) -> None:
    """Surfaced on the workflow run itself, so a skip is visible without opening the log
    and reading to the end of it."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::notice title=Integration::{message}")
        return
    print(f"==> {message}")

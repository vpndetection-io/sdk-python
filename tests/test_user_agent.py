"""The user agent a lookup sends, and the middleware's `allow_bots`.

An answer to a lookup that sent an agent carries that agent's verdict and nothing else
differs, so the cache and the requests in flight key on the pair: an answer is never
served for the address alone or for another agent.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
import threading
import time
from typing import Any

import httpx
import pytest
from helpers import ClientFactory

from vpndetection import AsyncVPNDetection, UserAgent, VPNDetection
from vpndetection._core import batch_request
from vpndetection._generated.models.batch_lookup_request import BatchLookupRequest
from vpndetection.middleware import (
    MAX_AGENTS_PER_ADDRESS,
    AsyncCore,
    Core,
    Guard,
    Lookup,
    Options,
    names_crawler,
)
from vpndetection.middleware.core import _CrawlerAgents

CORPUS = json.loads((pathlib.Path(__file__).parent.parent / "testdata/testdata.json").read_text())[
    "crawlerAgents"
]
PUBLIC_IP = "45.83.91.1"
PEER = "66.249.66.1"
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
CHROME = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)


WATCHED = {"ip": [PEER, "66.249.66.2"]}


def crawler(n: int) -> str:
    return f"Mozilla/5.0 (compatible; Examplebot/{n}.0)"


class Origin:
    """Answers every lookup, a batch's entries included, with the verdict `verdicts` holds
    for the agent it was sent, and records what each request carried. `delay` holds each
    answer back, so concurrent callers overlap."""

    def __init__(
        self,
        delay: float = 0.0,
        verdicts: dict[str, str] | None = None,
        *,
        verdict: str = "not_bot",
        bot: dict[str, Any] | None = None,
    ) -> None:
        self.requests: list[httpx.Request] = []
        self.verdicts = verdicts or {}
        self._verdict = verdict
        self._bot = bot
        self._delay = delay
        self._lock = threading.Lock()
        self.sync = httpx.MockTransport(self._handle_sync)
        self.aio = httpx.MockTransport(self._handle_async)

    def transport(self, kind: str) -> httpx.MockTransport:
        return self.sync if kind == "sync" else self.aio

    @property
    def agents(self) -> list[str | None]:
        """The `user_agent` each lookup sent, None where it sent none."""
        return [r.url.params.get("user_agent") for r in self.requests]

    @property
    def batches(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requests if r.url.path == "/batch"]

    def _handle_sync(self, request: httpx.Request) -> httpx.Response:
        self._record(request)
        time.sleep(self._delay)
        return self._answer(request)

    async def _handle_async(self, request: httpx.Request) -> httpx.Response:
        self._record(request)
        await asyncio.sleep(self._delay)
        return self._answer(request)

    def _record(self, request: httpx.Request) -> None:
        with self._lock:
            self.requests.append(request)

    def _body(self, ip: str, agent: str | None) -> dict[str, Any]:
        body: dict[str, Any] = {"ip": ip, "is_vpn": False}
        if self._bot is not None:
            body["bot"] = self._bot
        if agent:
            verdict = self.verdicts.get(agent, self._verdict)
            body["user_agent"] = {"agent": agent[:16], "kind": "bot", "verdict": verdict}
        return body

    def _answer(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/batch":
            sent = json.loads(request.content)
            agents = sent.get("user_agents") or {}
            results = {ip: self._body(ip, agents.get(ip)) for ip in sent["ips"]}
            return httpx.Response(200, json={"results": results, "errors": {}})
        ip = "9.9.9.9" if request.url.path == "/myip" else request.url.path.lstrip("/")
        return httpx.Response(200, json=self._body(ip, request.url.params.get("user_agent")))


# The base client: what reaches the origin.


def test_a_lookup_sends_its_agent_and_surfaces_the_verdict(make_client: ClientFactory) -> None:
    origin = Origin(verdicts={GOOGLEBOT: "verified"})
    client = make_client(transport=origin.transport(make_client.kind))

    result = client.lookup(PUBLIC_IP, user_agent=GOOGLEBOT)

    assert origin.agents == [GOOGLEBOT]
    assert result.user_agent == UserAgent(agent=GOOGLEBOT[:16], kind="bot", verdict="verified")


def test_my_ip_sends_its_agent_and_stays_uncached(make_client: ClientFactory) -> None:
    origin = Origin(verdicts={GOOGLEBOT: "spoofed"})
    client = make_client(transport=origin.transport(make_client.kind))

    first = client.my_ip(user_agent=GOOGLEBOT)
    client.my_ip(user_agent=GOOGLEBOT)

    assert [r.url.path for r in origin.requests] == ["/myip", "/myip"]
    assert origin.agents == [GOOGLEBOT, GOOGLEBOT]
    assert first.user_agent is not None
    assert first.user_agent.verdict == "spoofed"


def test_an_empty_agent_is_none(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind), cache=False)

    plain = client.lookup(PUBLIC_IP, user_agent="")
    client.my_ip(user_agent="")
    client.lookup_batch([PUBLIC_IP, "45.83.91.2"], user_agents={PUBLIC_IP: ""})

    assert [str(r.url) for r in origin.requests[:2]] == [
        f"https://api.vpndetection.io/{PUBLIC_IP}",
        "https://api.vpndetection.io/myip",
    ]
    assert "user_agents" not in origin.batches[0]
    assert plain.user_agent is None


def test_a_long_agent_is_sent_whole(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))
    agent = "A" * 2000

    client.lookup(PUBLIC_IP, user_agent=agent)

    assert origin.agents == [agent]


def test_an_agent_that_is_not_a_string_is_refused_before_anything_is_sent(
    make_client: ClientFactory,
) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    with pytest.raises(TypeError, match="user_agent"):
        client.lookup("10.0.0.1", user_agent=5)
    with pytest.raises(TypeError, match="user_agents"):
        client.lookup_batch([PUBLIC_IP], user_agents=[GOOGLEBOT])

    assert origin.requests == []


def test_a_bogon_carries_no_verdict_and_makes_no_request(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    single = client.lookup("10.0.0.1", user_agent=GOOGLEBOT)
    batched = client.lookup_batch(["10.0.0.2"], user_agents={"10.0.0.2": GOOGLEBOT})

    assert origin.requests == []
    assert single.user_agent == UserAgent()
    assert batched["10.0.0.2"].user_agent == UserAgent()


def test_the_cache_serves_an_answer_only_for_the_same_pair(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    client.lookup(PUBLIC_IP)
    client.lookup(PUBLIC_IP, user_agent="agent-a")
    again = client.lookup(PUBLIC_IP, user_agent="agent-a")
    client.lookup(PUBLIC_IP, user_agent="agent-b")
    plain = client.lookup(PUBLIC_IP)
    batched = client.lookup_batch([PUBLIC_IP], user_agents={PUBLIC_IP: "agent-a"})

    assert origin.agents == [None, "agent-a", "agent-b"]
    assert again.user_agent is not None
    assert plain.user_agent is None
    assert batched[PUBLIC_IP] is again


def test_a_batch_caches_each_entry_on_its_pair(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    client.lookup_batch([PUBLIC_IP, "45.83.91.2"], user_agents={PUBLIC_IP: "agent-a"})
    client.lookup(PUBLIC_IP, user_agent="agent-a")
    client.lookup("45.83.91.2")
    client.lookup(PUBLIC_IP)

    assert len(origin.requests) == 2, "a batch entry was not cached on its pair"
    assert origin.agents[1] is None


# The batch body.


def test_a_batch_sends_the_agents_keyed_as_sent_and_only_those_it_has(
    make_client: ClientFactory,
) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    answers = client.lookup_batch(
        ["::ffff:45.83.91.1", "45.83.91.2", "45.83.91.3"],
        user_agents={"::ffff:45.83.91.1": "agent-a", "45.83.91.3": "", "45.83.91.9": "agent-z"},
    )

    assert origin.batches == [
        {
            "ips": ["45.83.91.1", "45.83.91.2", "45.83.91.3"],
            "user_agents": {"45.83.91.1": "agent-a"},
        }
    ]
    assert answers["::ffff:45.83.91.1"].user_agent is not None
    assert answers["45.83.91.2"].user_agent is None


def test_a_batch_with_no_agent_sends_no_user_agents(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind))

    client.lookup_batch([PUBLIC_IP, "45.83.91.2"])
    client.lookup_batch(["45.83.91.3", "45.83.91.4"], user_agents={})

    assert [sorted(batch) for batch in origin.batches] == [["ips"], ["ips"]]


def test_each_chunk_sends_only_its_own_agents(make_client: ClientFactory) -> None:
    origin = Origin()
    client = make_client(transport=origin.transport(make_client.kind), concurrency=1)
    ips = [f"45.83.{n // 256}.{n % 256}" for n in range(1, 1201)]

    client.lookup_batch(ips, user_agents={ips[0]: "agent-a", ips[1100]: "agent-b"})
    client.lookup_batch(
        [f"45.84.{n // 256}.{n % 256}" for n in range(1, 1201)],
        user_agents={"45.84.0.1": "agent-c"},
    )

    batches = origin.batches
    assert [len(batch["ips"]) for batch in batches] == [1000, 200, 1000, 200]
    assert batches[0]["user_agents"] == {ips[0]: "agent-a"}
    assert batches[1]["user_agents"] == {ips[1100]: "agent-b"}
    assert batches[2]["user_agents"] == {"45.84.0.1": "agent-c"}
    assert "user_agents" not in batches[3], "a chunk with no agent sent user_agents"


def test_the_generated_batch_request_leaves_user_agents_out_when_unset() -> None:
    assert BatchLookupRequest(ips=[PUBLIC_IP]).to_dict() == {"ips": [PUBLIC_IP]}
    assert batch_request([PUBLIC_IP], {"45.83.91.2": "agent-a"}).to_dict() == {"ips": [PUBLIC_IP]}


# Sharing a request in flight: only for the same pair.


def _in_threads(*calls: Any) -> list[Any]:
    outcomes: list[Any] = [None] * len(calls)

    def run(n: int) -> None:
        outcomes[n] = calls[n]()

    threads = [threading.Thread(target=run, args=(n,)) for n in range(len(calls))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return outcomes


def test_sync_concurrent_misses_share_a_request_only_for_the_same_pair() -> None:
    origin = Origin(delay=0.2)
    with VPNDetection(transport=origin.sync) as client:
        outcomes = _in_threads(
            *[lambda: client.lookup(PUBLIC_IP, user_agent="agent-a")] * 10,
            *[lambda: client.lookup(PUBLIC_IP, user_agent="agent-b")] * 10,
            *[lambda: client.lookup(PUBLIC_IP)] * 10,
        )
    assert sorted(origin.agents, key=str) == sorted(["agent-a", "agent-b", None], key=str)
    assert [o.user_agent.agent if o.user_agent else None for o in outcomes] == (
        ["agent-a"] * 10 + ["agent-b"] * 10 + [None] * 10
    )


def test_async_concurrent_misses_share_a_request_only_for_the_same_pair() -> None:
    origin = Origin(delay=0.2)

    async def main() -> list[Any]:
        async with AsyncVPNDetection(transport=origin.aio) as client:
            return await asyncio.gather(
                *(client.lookup(PUBLIC_IP, user_agent="agent-a") for _ in range(10)),
                *(client.lookup(PUBLIC_IP, user_agent="agent-b") for _ in range(10)),
                *(client.lookup(PUBLIC_IP) for _ in range(10)),
            )

    outcomes = asyncio.run(main())
    assert sorted(origin.agents, key=str) == sorted(["agent-a", "agent-b", None], key=str)
    assert [o.user_agent.agent if o.user_agent else None for o in outcomes] == (
        ["agent-a"] * 10 + ["agent-b"] * 10 + [None] * 10
    )


def test_sync_a_batch_boards_a_lookup_in_flight_only_for_the_same_pair() -> None:
    origin = Origin(delay=0.3)
    with VPNDetection(transport=origin.sync) as client:

        def batch(agent: str) -> Any:
            time.sleep(0.1)
            return client.lookup_batch([PUBLIC_IP], user_agents={PUBLIC_IP: agent})

        _in_threads(
            lambda: client.lookup(PUBLIC_IP, user_agent="agent-a"),
            lambda: batch("agent-a"),
            lambda: batch("agent-b"),
        )
    assert len(origin.requests) == 2, "a batch shared another agent's request, or none"
    assert origin.batches == [{"ips": [PUBLIC_IP], "user_agents": {PUBLIC_IP: "agent-b"}}]


def test_async_a_lookup_boards_a_batch_in_flight_only_for_the_same_pair() -> None:
    origin = Origin(delay=0.3)

    async def main() -> None:
        async with AsyncVPNDetection(transport=origin.aio) as client:

            async def later(agent: str | None) -> Any:
                await asyncio.sleep(0.1)
                return await client.lookup(PUBLIC_IP, user_agent=agent)

            await asyncio.gather(
                client.lookup_batch([PUBLIC_IP], user_agents={PUBLIC_IP: "agent-a"}),
                later("agent-a"),
                later(None),
            )

    asyncio.run(main())
    assert len(origin.requests) == 2, "a lookup shared another agent's request, or none"
    assert origin.agents[1] is None


# The middleware's allow_bots, from a public peer.


class Req:
    def __init__(self, user_agent: str | None = GOOGLEBOT, ip: str = PUBLIC_IP) -> None:
        self.user_agent = user_agent
        self.ip = ip


def _core(origin: Origin, *, cache: bool = True, **options: Any) -> Core[Req]:
    client = VPNDetection(transport=origin.sync, cache=cache)
    return Core(Options(client=client, **options), lambda r: r.ip, lambda r: r.user_agent)


def test_allow_bots_sends_the_requests_own_agent() -> None:
    origin = Origin(verdicts={GOOGLEBOT: "verified"})
    core = _core(origin, allow_bots=True)

    found = core.evaluate(Req())

    assert origin.agents == [GOOGLEBOT]
    assert found is not None
    assert found.result is not None
    assert found.result.user_agent is not None


def test_allow_bots_sends_none_for_an_absent_or_empty_header() -> None:
    origin = Origin()
    core = _core(origin, allow_bots=True, on_missing_field="ignore")

    core.evaluate(Req(user_agent=None, ip="45.83.91.1"))
    core.evaluate(Req(user_agent="", ip="45.83.91.2"))

    assert origin.agents == [None, None]


def test_without_allow_bots_no_agent_is_sent() -> None:
    origin = Origin(verdicts={GOOGLEBOT: "verified"})
    core = _core(origin, block_condition={"ip": PUBLIC_IP})

    found = core.evaluate(Req())

    assert origin.agents == [None]
    assert found is not None
    assert found.blocked is True


@pytest.mark.parametrize(("verdict", "blocked"), [("verified", False), ("spoofed", True)])
@pytest.mark.parametrize("flavor", ["sync", "async"])
def test_a_verified_crawler_passes_a_condition_it_meets_and_a_forged_one_does_not(
    flavor: str, verdict: str, blocked: bool
) -> None:
    origin = Origin(verdicts={GOOGLEBOT: verdict})
    condition = {"ip": PUBLIC_IP}
    if flavor == "sync":
        found = _core(origin, allow_bots=True, block_condition=condition).evaluate(Req())
    else:

        async def run() -> Lookup | None:
            async with AsyncVPNDetection(transport=origin.aio) as client:
                core: AsyncCore[Req] = AsyncCore(
                    Options(client=client, allow_bots=True, block_condition=condition),
                    lambda r: r.ip,
                    lambda r: r.user_agent,
                )
                return await core.evaluate(Req())

        found = asyncio.run(run())
    assert found is not None
    assert found.blocked is blocked
    assert found.result is not None
    assert found.result.user_agent is not None
    assert found.result.user_agent.verdict == verdict


def test_a_condition_naming_user_agent_refuses_a_forged_crawler() -> None:
    origin = Origin(verdicts={GOOGLEBOT: "spoofed", crawler(1): "not_bot"})
    condition = {"user_agent": {"verdict": ["spoofed", "not_bot"]}}
    core = _core(origin, allow_bots=True, block_condition=condition)

    forged = core.evaluate(Req())
    script = core.evaluate(Req(user_agent=crawler(1), ip="45.83.91.2"))

    assert forged is not None
    assert forged.blocked is True
    assert script is not None
    assert script.blocked is True


def test_a_guard_never_refuses_a_verified_crawler() -> None:
    origin = Origin(verdicts={GOOGLEBOT: "verified", "curl/8": "not_bot"})
    core = _core(origin, allow_bots=True)
    guard = Guard({"ip": ["45.83.91.1", "45.83.91.2"]})

    verified = core.evaluate(Req())
    script = core.evaluate(Req(user_agent="curl/8", ip="45.83.91.2"))

    assert verified is not None
    assert guard.blocks(verified) is False
    assert script is not None
    assert guard.blocks(script) is True


def test_a_served_answer_without_a_verdict_warns_once() -> None:
    origin = Origin()
    origin.verdicts = {}
    warnings: list[str] = []

    def plain(request: httpx.Request) -> httpx.Response:
        origin.requests.append(request)
        return httpx.Response(200, json={"ip": request.url.path.lstrip("/"), "is_vpn": False})

    client = VPNDetection(transport=httpx.MockTransport(plain))
    core: Core[Req] = Core(
        Options(client=client, allow_bots=True, on_warn=warnings.append),
        lambda r: r.ip,
        lambda r: r.user_agent,
    )

    core.evaluate(Req(ip="45.83.91.1"))
    core.evaluate(Req(ip="45.83.91.2"))
    core.evaluate(Req(ip="10.0.0.1"))

    assert origin.agents == [GOOGLEBOT, GOOGLEBOT]
    unverified = [w for w in warnings if "user_agent verdict" in w]
    assert len(unverified) == 1, warnings


def test_only_an_agent_naming_a_crawler_is_sent_as_the_corpus_says() -> None:
    assert CORPUS["crawlers"] and CORPUS["others"]
    for agent in CORPUS["crawlers"]:
        assert names_crawler(agent) is True, agent
    for agent in CORPUS["others"]:
        assert names_crawler(agent) is False, agent
    for term in CORPUS["terms"]:
        assert names_crawler(f"x {term.upper()} y") is True, term
    assert names_crawler("BAR\u212aROWLER") is False, "only A-Z is folded to lower case"
    assert names_crawler("") is False

    origin = Origin(verdict="not_bot")
    found = _core(origin, allow_bots=True, block_condition=WATCHED).evaluate(
        Req(user_agent=CHROME, ip=PEER)
    )

    assert origin.agents == [None], "a browser's agent stayed off the lookup"
    assert found is not None
    assert found.blocked is True


def test_a_core_without_a_condition_sends_no_agent_for_a_browser_and_blocks_nothing() -> None:
    origin = Origin(verdict="verified")
    found = _core(origin, allow_bots=True, on_missing_field="ignore").evaluate(
        Req(user_agent=CHROME, ip=PEER)
    )

    assert origin.agents == [None]
    assert found is not None
    assert found.crawler is False


def test_one_address_is_looked_up_with_at_most_four_crawler_agents() -> None:
    assert MAX_AGENTS_PER_ADDRESS == 4
    origin = Origin(verdict="verified")
    core = _core(origin, cache=False, allow_bots=True, block_condition=WATCHED)

    def passes(agent: str, ip: str = PEER) -> bool:
        found = core.evaluate(Req(user_agent=agent, ip=ip))
        assert found is not None
        return not found.blocked

    for n in range(1, 5):
        assert passes(crawler(n)), f"agent {n}"
    assert not passes(crawler(5)), "an agent past the bound is never let through as verified"
    assert passes(crawler(1)), "a known agent is still sent"
    assert origin.agents == [crawler(1), crawler(2), crawler(3), crawler(4), None, crawler(1)]

    assert passes(crawler(5), "66.249.66.2"), "each address has its own bound"
    assert origin.agents[-1] == crawler(5)


def test_the_bound_holds_for_the_async_core_too() -> None:
    origin = Origin(verdict="verified")

    async def run() -> list[bool]:
        async with AsyncVPNDetection(transport=origin.aio, cache=False) as client:
            core: AsyncCore[Req] = AsyncCore(
                Options(client=client, allow_bots=True, block_condition=WATCHED),
                lambda r: r.ip,
                lambda r: r.user_agent,
            )
            outcomes = []
            for n in [1, 2, 3, 4, 5, 1]:
                found = await core.evaluate(Req(user_agent=crawler(n), ip=PEER))
                assert found is not None
                outcomes.append(found.blocked)
            return outcomes

    assert asyncio.run(run()) == [False, False, False, False, True, False]
    assert origin.agents == [crawler(1), crawler(2), crawler(3), crawler(4), None, crawler(1)]


def test_past_the_bound_an_address_its_operator_vouches_for_still_passes() -> None:
    origin = Origin(verdict="verified", bot={"verified": True})
    core = _core(origin, allow_bots=True, block_condition=WATCHED)

    for n in range(1, 6):
        found = core.evaluate(Req(user_agent=crawler(n), ip=PEER))
        assert found is not None
        assert found.blocked is False, f"agent {n}"
    assert origin.agents[-1] is None

    browser = core.evaluate(Req(user_agent=CHROME, ip=PEER))
    assert browser is not None
    assert browser.blocked is True, "a browser on that address is judged as the condition says"


def test_a_guard_passes_a_request_the_middleware_passed_past_the_bound() -> None:
    origin = Origin(verdict="verified", bot={"verified": True})
    core = _core(origin, allow_bots=True)
    guard = Guard(WATCHED)

    for n in range(1, 6):
        found = core.evaluate(Req(user_agent=crawler(n), ip=PEER))
        assert found is not None
        assert guard.blocks(found) is False, f"agent {n}"
    browser = core.evaluate(Req(user_agent=CHROME, ip=PEER))
    assert browser is not None
    assert guard.blocks(browser) is True


def test_no_unsent_agent_reports_a_missing_verdict() -> None:
    warnings: list[str] = []
    origin = Origin(bot={"verified": False})
    core = _core(origin, allow_bots=True, on_warn=warnings.append)

    for n in range(1, 6):
        core.evaluate(Req(user_agent=crawler(n), ip=PEER))
    core.evaluate(Req(user_agent=CHROME, ip=PEER))

    assert origin.agents[4:] == [None], "the address-only answer is cached, whoever asked"
    assert warnings == [], "a lookup that sent no agent has no verdict to lack"


def test_an_address_is_remembered_an_hour_from_its_first_agent() -> None:
    now = [1000.0]
    agents = _CrawlerAgents(timer=lambda: now[0])

    for n in range(1, 5):
        assert agents.agent_for(PEER, crawler(n)) == crawler(n)
        now[0] += 500.0
    now[0] = 1000.0 + 3599.0
    assert agents.agent_for(PEER, crawler(5)) is None, "still held just under the hour"
    assert agents.agent_for(PEER, crawler(1)) == crawler(1)
    now[0] = 1000.0 + 3601.0
    assert agents.agent_for(PEER, crawler(5)) == crawler(5), "adding agents did not extend it"
    assert agents.agent_for(PEER, crawler(6)) == crawler(6)


def test_the_remembered_addresses_are_bounded() -> None:
    agents = _CrawlerAgents()
    for n in range(10_050):
        agents.agent_for(f"2001:db8::{n:x}", crawler(1))
    assert len(agents._entries) == 10_000


def test_a_core_without_a_user_agent_selector_refuses_allow_bots() -> None:
    with pytest.raises(ValueError, match="allow_bots"):
        Core(Options(allow_bots=True), lambda r: PUBLIC_IP)

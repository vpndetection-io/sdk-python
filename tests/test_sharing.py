"""Concurrent misses for one address share one request, a batch's included.

Driven on the clients themselves rather than the one-surface adapter, which runs each
async call in an event loop of its own: sharing needs the callers in one.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import httpx
import pytest

from vpndetection import AsyncVPNDetection, VPNDetection, VPNDetectionError

# Long enough that a call started a quarter of it later is still concurrent.
STAGGER = 0.4


class Origin:
    """Answers after a delay, and records each path and each batch's addresses, so a
    request shared or sent twice shows in the count."""

    def __init__(self, delay: float, refuse: set[str] | None = None) -> None:
        self.paths: list[str] = []
        self.batched: list[list[str]] = []
        self.refuse = refuse if refuse is not None else set()
        self._delay = delay
        self._lock = threading.Lock()
        self.sync = httpx.MockTransport(self._handle_sync)
        self.aio = httpx.MockTransport(self._handle_async)

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
            self.paths.append(request.url.path)
            if request.url.path == "/batch":
                self.batched.append(json.loads(request.content)["ips"])

    def _answer(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/batch":
            results: dict[str, Any] = {}
            errors: dict[str, Any] = {}
            for ip in json.loads(request.content)["ips"]:
                if ip in self.refuse:
                    errors[ip] = {"status": 403, "error": "forbidden"}
                else:
                    results[ip] = {"ip": ip, "is_vpn": False}
            return httpx.Response(200, json={"results": results, "errors": errors})
        ip = request.url.path.lstrip("/")
        if ip in self.refuse:
            return httpx.Response(403, json={"error": "forbidden"})
        return httpx.Response(200, json={"ip": ip, "is_vpn": False})


def in_threads(*calls: Any) -> list[Any]:
    """Runs each call on a thread of its own, the nth started n quarter-staggers in when
    asked, and returns each outcome, an exception included."""
    with ThreadPoolExecutor(max_workers=len(calls)) as pool:
        futures = [pool.submit(call) for call in calls]
        outcomes: list[Any] = []
        for future in futures:
            try:
                outcomes.append(future.result())
            except Exception as err:  # noqa: BLE001 - the outcome is what is asserted
                outcomes.append(err)
    return outcomes


def later(call: Any) -> Any:
    def run() -> Any:
        time.sleep(STAGGER / 4)
        return call()

    return run


def test_sync_concurrent_misses_for_one_address_share_one_request() -> None:
    origin = Origin(0.2)
    with VPNDetection(transport=origin.sync) as client:
        outcomes = in_threads(*[lambda: client.lookup("45.83.91.1")] * 20)
    assert origin.paths == ["/45.83.91.1"], f"20 callers sent {len(origin.paths)} requests"
    assert all(outcome.ip == "45.83.91.1" for outcome in outcomes)


def test_async_concurrent_misses_for_one_address_share_one_request() -> None:
    origin = Origin(0.2)

    async def main() -> list[Any]:
        async with AsyncVPNDetection(transport=origin.aio) as client:
            return await asyncio.gather(*(client.lookup("45.83.91.1") for _ in range(20)))

    outcomes = asyncio.run(main())
    assert origin.paths == ["/45.83.91.1"], f"20 callers sent {len(origin.paths)} requests"
    assert all(outcome.ip == "45.83.91.1" for outcome in outcomes)


def test_sync_a_shared_failure_reaches_every_waiter_and_is_not_cached() -> None:
    origin = Origin(0.2, refuse={"45.83.91.1"})
    with VPNDetection(transport=origin.sync, retries=0) as client:
        outcomes = in_threads(*[lambda: client.lookup("45.83.91.1")] * 5)
        assert len(origin.paths) == 1
        for outcome in outcomes:
            assert isinstance(outcome, VPNDetectionError)
            assert outcome.kind == "forbidden"
        assert len({id(outcome) for outcome in outcomes}) == 5, "waiters raised one instance"
        origin.refuse.clear()
        assert client.lookup("45.83.91.1").ip == "45.83.91.1"
    assert len(origin.paths) == 2, "the failure was cached"


def test_sync_a_batch_awaits_a_lookup_in_flight() -> None:
    origin = Origin(STAGGER)
    with VPNDetection(transport=origin.sync) as client:
        _, batch = in_threads(
            lambda: client.lookup("45.83.91.1"),
            later(lambda: client.lookup_batch(["45.83.91.1", "45.83.91.2"])),
        )
    assert batch["45.83.91.1"].ip == "45.83.91.1"
    assert origin.batched == [["45.83.91.2"]], "the batch sent the address in flight again"
    assert len(origin.paths) == 2


def test_async_a_batch_awaits_a_lookup_in_flight() -> None:
    origin = Origin(STAGGER)

    async def main() -> Any:
        async with AsyncVPNDetection(transport=origin.aio) as client:

            async def batch() -> Any:
                await asyncio.sleep(STAGGER / 4)
                return await client.lookup_batch(["45.83.91.1", "45.83.91.2"])

            return (await asyncio.gather(client.lookup("45.83.91.1"), batch()))[1]

    answers = asyncio.run(main())
    assert answers["45.83.91.1"].ip == "45.83.91.1"
    assert origin.batched == [["45.83.91.2"]], "the batch sent the address in flight again"


def test_sync_a_lookup_takes_the_answer_of_the_batch_it_joined() -> None:
    origin = Origin(STAGGER, refuse={"45.83.91.2"})
    with VPNDetection(transport=origin.sync) as client:
        _, served, refused = in_threads(
            lambda: client.lookup_batch(["45.83.91.1", "45.83.91.2"]),
            later(lambda: client.lookup("45.83.91.1")),
            later(lambda: client.lookup("45.83.91.2")),
        )
    assert served.ip == "45.83.91.1"
    assert isinstance(refused, VPNDetectionError) and refused.kind == "forbidden"
    assert origin.paths == ["/batch"]


def test_async_a_lookup_takes_the_answer_of_the_batch_it_joined() -> None:
    origin = Origin(STAGGER, refuse={"45.83.91.2"})

    async def main() -> Any:
        async with AsyncVPNDetection(transport=origin.aio) as client:

            async def lookup(ip: str) -> Any:
                await asyncio.sleep(STAGGER / 4)
                try:
                    return await client.lookup(ip)
                except VPNDetectionError as err:
                    return err

            return await asyncio.gather(
                client.lookup_batch(["45.83.91.1", "45.83.91.2"]),
                lookup("45.83.91.1"),
                lookup("45.83.91.2"),
            )

    _, served, refused = asyncio.run(main())
    assert served.ip == "45.83.91.1"
    assert isinstance(refused, VPNDetectionError) and refused.kind == "forbidden"
    assert origin.paths == ["/batch"]


def test_async_a_waiter_outlives_the_leader_it_joined_and_its_own_cancel_is_its_own() -> None:
    origin = Origin(STAGGER)

    async def main() -> Any:
        async with AsyncVPNDetection(transport=origin.aio) as client:
            leader = asyncio.ensure_future(client.lookup("45.83.91.1"))
            await asyncio.sleep(STAGGER / 8)
            quitter = asyncio.ensure_future(client.lookup("45.83.91.1"))
            waiter = asyncio.ensure_future(client.lookup("45.83.91.1"))
            await asyncio.sleep(STAGGER / 8)
            quitter.cancel()
            leader.cancel()
            with pytest.raises(asyncio.CancelledError):
                await leader
            with pytest.raises(asyncio.CancelledError):
                await quitter
            return await waiter

    assert asyncio.run(main()).ip == "45.83.91.1"
    assert len(origin.paths) == 2, "the waiter should have asked again, once"


@pytest.mark.parametrize("kind", ["sync", "async"])
def test_a_client_without_a_cache_shares_nothing(kind: str) -> None:
    origin = Origin(0.1)
    if kind == "sync":
        with VPNDetection(transport=origin.sync, cache=False) as client:
            in_threads(
                *[lambda: client.lookup("45.83.91.1")] * 3,
                *[lambda: client.lookup_batch(["45.83.91.1"])] * 2,
            )
    else:

        async def main() -> None:
            async with AsyncVPNDetection(transport=origin.aio, cache=False) as client:
                await asyncio.gather(
                    *(client.lookup("45.83.91.1") for _ in range(3)),
                    *(client.lookup_batch(["45.83.91.1"]) for _ in range(2)),
                )

        asyncio.run(main())
    assert len(origin.paths) == 5

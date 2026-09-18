"""Test doubles and corpus loading, shared by both test modules.

Every corpus assertion runs against BOTH clients. `ClientAdapter` drives the async one
through the synchronous surface so the corpus is written once: two bindings that disagree
with each other are exactly what the corpus exists to catch, and asserting only the sync
client would leave half of this library unchecked.
"""

from __future__ import annotations

import asyncio
import dataclasses
import datetime
import json
import socket
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn, Self, cast

import httpx
import pytest

from vpndetection import AsyncVPNDetection, Result, VPNDetection
from vpndetection._core import AsyncClock, Clock

TESTDATA: dict[str, Any] = json.loads(
    (Path(__file__).resolve().parent.parent / "testdata" / "testdata.json").read_text()
)


class ClientFactory:
    """Builds clients of one flavor and closes every one of them afterwards.

    Carries `kind` because a test double sometimes has to know which flavor it is about
    to serve: a handler that blocks a thread is right for the sync client and wrong for
    the async one, where it would serialize the very thing under test.
    """

    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._built: list[ClientAdapter] = []

    def __call__(self, **options: Any) -> ClientAdapter:
        adapter = ClientAdapter(self.kind, **options)
        self._built.append(adapter)
        return adapter

    def close_all(self) -> None:
        for adapter in self._built:
            adapter.close()


class ClientAdapter:
    """One synchronous surface over both clients."""

    def __init__(self, kind: str, **options: Any) -> None:
        self.kind = kind
        self.client: VPNDetection | AsyncVPNDetection = (
            VPNDetection(**options) if kind == "sync" else AsyncVPNDetection(**options)
        )
        self.database = DatabaseAdapter(self.client)
        self.oauth = OauthAdapter(self.client)

    def is_bogon(self, ip: str) -> bool:
        return self.client.is_bogon(ip)

    def lookup(self, ip: str, **kwargs: Any) -> Result:
        if isinstance(self.client, VPNDetection):
            return self.client.lookup(ip, **kwargs)
        return asyncio.run(self.client.lookup(ip, **kwargs))

    def my_ip(self, **kwargs: Any) -> Result:
        if isinstance(self.client, VPNDetection):
            return self.client.my_ip(**kwargs)
        return asyncio.run(self.client.my_ip(**kwargs))

    def my_entitlement(self, **kwargs: Any) -> Any:
        if isinstance(self.client, VPNDetection):
            return self.client.my_entitlement(**kwargs)
        return asyncio.run(self.client.my_entitlement(**kwargs))

    def lookup_batch(self, ips: Any, **kwargs: Any) -> dict[str, Any]:
        if isinstance(self.client, VPNDetection):
            return self.client.lookup_batch(ips, **kwargs)
        return asyncio.run(self.client.lookup_batch(ips, **kwargs))

    def close(self) -> None:
        if isinstance(self.client, VPNDetection):
            self.client.close()
        else:
            asyncio.run(self.client.aclose())


class DatabaseAdapter:
    """The `database` surface of whichever client this run is exercising.

    The download path is not one method shared by two clients: the async one writes each
    chunk from a worker thread rather than blocking the event loop, so it is genuinely
    different code and has to be asserted as such.
    """

    def __init__(self, client: VPNDetection | AsyncVPNDetection) -> None:
        self._client = client

    def list(self, **kwargs: Any) -> Any:
        return self._call("list", **kwargs)

    def metadata(self, dataset_id: str, **kwargs: Any) -> Any:
        return self._call("metadata", dataset_id, **kwargs)

    def checksums(self, dataset_id: str, format: str, **kwargs: Any) -> Any:
        return self._call("checksums", dataset_id, format, **kwargs)

    def downloads(self, *args: Any, **kwargs: Any) -> Any:
        return self._call("downloads", *args, **kwargs)

    def download_url(self, dataset_id: str, format: str, **kwargs: Any) -> str:
        return cast(str, self._call("download_url", dataset_id, format, **kwargs))

    def download(self, dataset_id: str, format: str, path: Any, **kwargs: Any) -> int:
        return cast(int, self._call("download", dataset_id, format, path, **kwargs))

    def download_bytes(self, dataset_id: str, format: str, **kwargs: Any) -> bytes:
        return cast(bytes, self._call("download_bytes", dataset_id, format, **kwargs))

    # Keyword arguments are forwarded untouched and none is named here: a `timeout`
    # in this signature would swallow the TypeError a transfer must raise for one.
    def _call(self, name: str, *args: Any, **kwargs: Any) -> Any:
        method = getattr(self._client.database, name)
        if isinstance(self._client, VPNDetection):
            return method(*args, **kwargs)
        return asyncio.run(method(*args, **kwargs))


class OauthAdapter:
    """The `oauth` surface of whichever client this run is exercising."""

    def __init__(self, client: VPNDetection | AsyncVPNDetection) -> None:
        self._client = client

    def use_clock(self, clock: FakeClock) -> None:
        if isinstance(self._client, VPNDetection):
            self._client.oauth._clock = clock
        else:
            self._client.oauth._clock = AsyncFakeClock(clock)

    def metadata(self, **kwargs: Any) -> Any:
        return self._call("metadata", **kwargs)

    def device_authorization(self, client_id: str, **kwargs: Any) -> Any:
        return self._call("device_authorization", client_id, **kwargs)

    def exchange_device_code(self, client_id: str, device_code: str, **kwargs: Any) -> Any:
        return self._call("exchange_device_code", client_id, device_code, **kwargs)

    def exchange_refresh_token(self, client_id: str, refresh_token: str, **kwargs: Any) -> Any:
        return self._call("exchange_refresh_token", client_id, refresh_token, **kwargs)

    def revoke(self, client_id: str, token: str, **kwargs: Any) -> Any:
        return self._call("revoke", client_id, token, **kwargs)

    def poll_device_token(self, client_id: str, device: Any, **kwargs: Any) -> Any:
        return self._call("poll_device_token", client_id, device, **kwargs)

    def _call(self, name: str, *args: Any, **kwargs: Any) -> Any:
        method = getattr(self._client.oauth, name)
        if isinstance(self._client, VPNDetection):
            return method(*args, **kwargs)
        return asyncio.run(method(*args, **kwargs))


# Past this many requests, waits or clock reads, a loop under test fails its test.
LOOP_BOUND = 16


class LoopBound:
    """Ends a test whose code under test does not end.

    Past its cap a stub or a fake clock calls `trip`, which BLOCKS for good rather than
    raising: an exception can be swallowed by the very loop it is meant to stop, a wait
    cannot. `settle` notices the trip and fails the test from outside the call.
    """

    def __init__(self) -> None:
        self.why = ""
        self.tripped = threading.Event()

    def trip(self, why: str) -> NoReturn:
        self.why = why
        self.tripped.set()
        threading.Event().wait()
        raise AssertionError("unreachable")


def settle(call: Callable[[], Any], bound: LoopBound, within: float = 15.0) -> Any:
    """What `call` returned, or the exception it raised, run on a thread of its own so a
    call that never ends fails the test instead of hanging the suite."""
    outcome: list[Any] = []

    def run() -> None:
        try:
            outcome.append(call())
        except BaseException as exc:  # noqa: BLE001 - the outcome under test
            outcome.append(exc)

    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    give_up = time.monotonic() + within
    while worker.is_alive():
        if bound.tripped.is_set():
            pytest.fail(f"{bound.why}: the call under test does not end")
        if time.monotonic() > give_up:
            pytest.fail(f"the call under test did not settle within {within}s")
        worker.join(0.02)
    return outcome[0]


class FakeClock(Clock):
    """A poll's sleep and monotonic clock, replaced together, recording every wait in
    seconds. Past LOOP_BOUND waits, or twice that many clock reads, it trips `bound`."""

    def __init__(self, bound: LoopBound) -> None:
        self.waits: list[float] = []
        self._elapsed = 0.0
        self._reads = 0
        self._bound = bound

    def now(self) -> float:
        self._reads += 1
        if self._reads > 2 * LOOP_BOUND:
            self._bound.trip(f"read the clock {self._reads} times")
        return self._elapsed

    def sleep(self, seconds: float) -> None:
        if len(self.waits) == LOOP_BOUND:
            self._bound.trip(f"waited more than {LOOP_BOUND} times")
        self.waits.append(seconds)
        self._elapsed += seconds


class AsyncFakeClock(AsyncClock):
    """`FakeClock`, for the async client."""

    def __init__(self, clock: FakeClock) -> None:
        self._clock = clock

    def now(self) -> float:
        return self._clock.now()

    async def sleep(self, seconds: float) -> None:
        self._clock.sleep(seconds)


class OauthStub:
    """Answers from a list of replies in order, repeating the last, and keeps every request
    that left the client. Past `limit` requests it trips `bound` rather than answering."""

    def __init__(
        self, replies: list[dict[str, Any]], bound: LoopBound, limit: int = LOOP_BOUND
    ) -> None:
        self.requests: list[httpx.Request] = []
        self.transport = httpx.MockTransport(self._handle)
        self._replies = replies
        self._bound = bound
        self._limit = limit

    def _handle(self, request: httpx.Request) -> httpx.Response:
        if len(self.requests) == self._limit:
            self._bound.trip(f"sent more than {self._limit} request(s)")
        self.requests.append(request)
        reply = self._replies[min(len(self.requests), len(self._replies)) - 1]
        body = reply["rawBody"] if "rawBody" in reply else json.dumps(reply["body"])
        return httpx.Response(
            reply["status"], content=body.encode(), headers={"content-type": "application/json"}
        )


class Stub:
    """A transport that answers from a table and records what it was asked for, so
    "never touched the network" is asserted rather than assumed."""

    def __init__(self, routes: dict[str, dict[str, Any]]) -> None:
        self.routes = routes
        self.calls: list[str] = []
        self.transport = httpx.MockTransport(self._handle)

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(f"{request.method} {request.url}")
        if request.url.path == "/batch":
            return self._batch(request)
        ip = _ip_of(request)
        route = self.routes.get(ip)
        if route is None:
            return httpx.Response(400, json={"error": "not a valid IP address"})
        return httpx.Response(
            route.get("status", 200), json=route["body"], headers=route.get("headers")
        )

    # A POST /batch is answered the way the API answers one: every address the table
    # knows is a result if its route is a 200 and an entry error otherwise, and an
    # unknown address is the 400 the API gives a string that is not one.
    def _batch(self, request: httpx.Request) -> httpx.Response:
        results: dict[str, Any] = {}
        errors: dict[str, Any] = {}
        for ip in json.loads(request.content or b"{}").get("ips", []):
            route = self.routes.get(ip)
            if route is None:
                errors[ip] = {"status": 400, "error": "not a valid IP address"}
            elif route.get("status", 200) == 200:
                results[ip] = route["body"]
            else:
                errors[ip] = {"status": route["status"], "error": route["body"].get("error")}
        return httpx.Response(200, json={"results": results, "errors": errors})


class Meter:
    """A transport that answers slowly enough for concurrent calls to overlap, and
    records the peak number in flight.

    Asserting the PEAK is the only way to tell a real limit from an option that was
    accepted and ignored. The sync client drives this from a thread pool, so the counters
    need a lock; the async one drives it from one event loop, where they do not.
    """

    def __init__(self, kind: str, delay: float = 0.02) -> None:
        self.in_flight = 0
        self.peak = 0
        self.calls = 0
        self._lock = threading.Lock()
        handler = self._handle_sync if kind == "sync" else self._handle_async
        self.transport = httpx.MockTransport(handler)
        self._delay = delay

    def _handle_sync(self, request: httpx.Request) -> httpx.Response:
        self._enter()
        time.sleep(self._delay)
        return self._leave(request)

    async def _handle_async(self, request: httpx.Request) -> httpx.Response:
        self._enter()
        await asyncio.sleep(self._delay)
        return self._leave(request)

    def _enter(self) -> None:
        with self._lock:
            self.calls += 1
            self.in_flight += 1
            self.peak = max(self.peak, self.in_flight)

    def _leave(self, request: httpx.Request) -> httpx.Response:
        with self._lock:
            self.in_flight -= 1
        # A batch arrives as one POST per chunk, so it is answered from the addresses in
        # the body rather than from the path.
        if request.url.path == "/batch":
            ips = json.loads(request.content or b"{}").get("ips", [])
            return httpx.Response(
                200,
                json={"results": {ip: {"ip": ip, "is_vpn": False} for ip in ips}, "errors": {}},
            )
        return httpx.Response(200, json={"ip": _ip_of(request), "is_vpn": False})


class Stall:
    """A local listener that never answers, so the only thing that can end a request to it
    is a timeout.

    A real socket rather than a `MockTransport`, because httpx enforces a timeout in its
    network transport and a mock transport never consults one. Nothing calls `accept`: the
    kernel completes the handshake regardless, so the request goes out and the read stalls.
    """

    def __init__(self) -> None:
        self._listener = socket.create_server(("127.0.0.1", 0))
        host, port = self._listener.getsockname()[:2]
        self.url = f"http://{host}:{port}"

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._listener.close()


class SlowBody:
    """A local server that answers every request with a 200's headers and the first byte of
    its body, then sends a byte every `trickle` seconds, or nothing more when that is None.

    What httpx's own timeout cannot bound: it limits each read rather than the attempt, so a
    trickle faster than the bound resets it forever. A mocked transport would not do, since
    it never consults a timeout. Each response gives up after `for_at_most` seconds, so a
    client that stops honoring its bound fails its test instead of hanging the suite.
    """

    def __init__(self, trickle: float | None, for_at_most: float = 3.0) -> None:
        self._listener = socket.create_server(("127.0.0.1", 0))
        self._listener.settimeout(0.05)
        host, port = self._listener.getsockname()[:2]
        self.url = f"http://{host}:{port}"
        self._trickle = trickle
        self._for_at_most = for_at_most
        self._closed = threading.Event()
        threading.Thread(target=self._serve, daemon=True).start()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._closed.set()
        self._listener.close()

    def _serve(self) -> None:
        while not self._closed.is_set():
            try:
                conn, _ = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            threading.Thread(target=self._answer, args=(conn,), daemon=True).start()

    def _answer(self, conn: socket.socket) -> None:
        give_up = time.monotonic() + self._for_at_most
        with conn:
            try:
                conn.settimeout(self._for_at_most)
                conn.recv(65536)
                conn.sendall(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    b"Content-Length: 100000\r\n\r\n{"
                )
                gap = self._for_at_most if self._trickle is None else self._trickle
                while not self._closed.wait(gap) and time.monotonic() < give_up:
                    if self._trickle is not None:
                        conn.sendall(b" ")
            except OSError:
                return


def as_wire(detail: Any) -> dict[str, Any]:
    """A detail object back in the shape the corpus writes it in.

    The corpus is language-neutral JSON, so its dates are ISO strings; this library hands
    a Python caller `datetime.date`, which is the whole reason this exists.
    """
    fields = dataclasses.asdict(detail)
    return {
        key: value.isoformat() if isinstance(value, datetime.date) else value
        for key, value in fields.items()
        if value is not None
    }


def _ip_of(request: httpx.Request) -> str:
    return request.url.path.lstrip("/")

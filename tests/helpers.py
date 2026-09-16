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
from pathlib import Path
from typing import Any, Self

import httpx

from vpndetection import AsyncVPNDetection, Result, VPNDetection

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

    def download_url(self, dataset_id: str, format: str) -> str:
        return self._call("download_url", dataset_id, format)  # type: ignore[no-any-return]

    def download(self, dataset_id: str, format: str, path: Any) -> int:
        return self._call("download", dataset_id, format, path)  # type: ignore[no-any-return]

    def download_bytes(self, dataset_id: str, format: str) -> bytes:
        return self._call("download_bytes", dataset_id, format)  # type: ignore[no-any-return]

    def _call(self, name: str, *args: Any) -> Any:
        method = getattr(self._client.database, name)
        if isinstance(self._client, VPNDetection):
            return method(*args)
        return asyncio.run(method(*args))


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

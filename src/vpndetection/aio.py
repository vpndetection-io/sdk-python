"""The asyncio client.

Mirrors `client.py` field for field; only the waiting differs. The two are written out
rather than shared because every difference between them is an `await`, and the wrappers
that hide that are harder to read than the duplication.
"""

from __future__ import annotations

import asyncio
import builtins
import os
from collections.abc import Awaitable, Callable, Iterable
from types import TracebackType
from typing import Any, Self, TypeVar

import httpx

from ._core import (
    BATCH_MAX,
    DEFAULT_BASE_URL,
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_CONCURRENCY,
    DEFAULT_DOWNLOADS_LIMIT,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    DEVICE_CODE_GRANT,
    OAUTH_DEVICE_AUTHORIZATION_PATH,
    OAUTH_METADATA_PATH,
    OAUTH_REVOKE_PATH,
    OAUTH_TOKEN_PATH,
    TRANSFER_CHUNK_BYTES,
    AsyncClock,
    Cache,
    as_error,
    assert_whole_transfer,
    batch_answers,
    build_async_transfer_client,
    build_client,
    check_concurrency,
    check_timeout,
    checksums_of,
    chunked,
    databases_of,
    downloads_of,
    oauth_body,
    oauth_request_async,
    parse_body,
    part_file,
    redirect_location,
    request_async,
    retry_delay,
    storage_refusal,
    unwrap,
)
from ._generated.api.database import (
    database_checksum,
    database_metadata,
    download_database,
    list_databases,
    list_downloads,
)
from ._generated.api.entitlement import my_entitlement
from ._generated.api.lookup import lookup_batch, lookup_ip, lookup_my_ip
from ._generated.client import AuthenticatedClient
from ._generated.models.batch_lookup_request import BatchLookupRequest
from ._generated.models.database import Database
from ._generated.models.database_format import DatabaseFormat
from ._generated.models.database_metadata import DatabaseMetadata
from ._generated.models.download import Download
from ._generated.models.entitlement import Entitlement
from .bogon import bogon_result, is_bogon
from .errors import OauthError, OauthExpiredTokenError, VPNDetectionError
from .models import (
    DeviceAuthorization,
    Format,
    OauthMetadata,
    Result,
    TokenResponse,
    to_device_authorization,
    to_oauth_metadata,
    to_result,
    to_token_response,
)

__all__ = ["AsyncDatabaseApi", "AsyncOauthApi", "AsyncVPNDetection"]

T = TypeVar("T")


class AsyncVPNDetection:
    """A client for the VPNDetection API, for asyncio.

    Identical in behavior to `VPNDetection`, including the per-instance cache and the
    bogon short-circuit. Close it with `await client.aclose()`, or use it as an async
    context manager.
    """

    database: AsyncDatabaseApi

    oauth: AsyncOauthApi
    """The licensed dataset downloads, for keys that carry the `db.download` scope."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        cache: bool = True,
        cache_max_size: int = DEFAULT_CACHE_MAX_SIZE,
        cache_ttl: float = DEFAULT_CACHE_TTL,
        concurrency: int = DEFAULT_CONCURRENCY,
        retries: int = DEFAULT_RETRIES,
        timeout: float | None = DEFAULT_TIMEOUT,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        timeout = check_timeout(timeout)
        self._client = build_client(api_key, base_url, timeout, transport)
        self._transfer = build_async_transfer_client(timeout, transport)
        self._cache = Cache(cache_max_size, cache_ttl) if cache else None
        self._concurrency = concurrency
        self._retries = retries
        self._timeout = timeout
        self.database = AsyncDatabaseApi(self)
        self.oauth = AsyncOauthApi(self)

    def is_bogon(self, ip: str) -> bool:
        """Whether an address is private, loopback, link-local, documentation, multicast
        or otherwise not routable, including the IPv6 equivalents and the 6to4 and
        Teredo ranges.

        Answered from a local table, so it is a plain function rather than a coroutine.
        """
        return is_bogon(ip)

    async def lookup(
        self, ip: str, *, retries: int | None = None, timeout: float | None = None
    ) -> Result:
        """Classify one address.

        A bogon is answered locally and never reaches the network. Everything else is
        served, then cached for this instance.
        """
        # Here as well as in _bound: a bogon or a cached answer returns before any request.
        check_timeout(timeout)
        if is_bogon(ip):
            return bogon_result(ip)
        if self._cache is not None:
            hit = self._cache.get(ip)
            if hit is not None:
                return hit

        async def call() -> Result:
            res = await request_async(lookup_ip, self._client, self._bound(timeout), ip=ip)
            return parse_body(unwrap(res), to_result)

        result = await self._retrying(call, self._retries if retries is None else retries)
        if self._cache is not None:
            self._cache.put(ip, result)
        return result

    async def my_ip(self, *, retries: int | None = None, timeout: float | None = None) -> Result:
        """Classify the address this client is calling from.

        The same answer `lookup` would give for that address, at the same cost against
        your allowance. The address is the one our edge observed, so a call made through
        a proxy or a VPN reports the exit it left through - usually the point of asking.

        Deliberately NOT cached. The cache is keyed by address, and which address this
        is IS the question: a machine that moves between networks would otherwise be
        told where it used to be.
        """

        async def call() -> Result:
            res = await request_async(lookup_my_ip, self._client, self._bound(timeout))
            return parse_body(unwrap(res), to_result)

        return await self._retrying(call, self._retries if retries is None else retries)

    async def my_entitlement(
        self, *, retries: int | None = None, timeout: float | None = None
    ) -> Entitlement:
        """What this client's key is entitled to, and how much of it has been used.

        Named for what it answers rather than `me`, which sits one letter from `my_ip`
        and means something quite different: one is which address you are calling FROM,
        the other is what the key you are calling WITH may spend.

        Unlike a lookup there is no useful unauthenticated answer, so a client built
        without a key gets an unauthorized error rather than a partial one.

        Usage counts against the ALLOWANCE WINDOW - the anniversary of the subscription,
        not the calendar month and not the billing period - and it is the same number a
        lookup is gated on. It can lag by a few seconds, because requests are counted in
        memory and flushed in aggregate.

        Deliberately NOT cached: the whole point is what has been spent, and a cached
        answer is a wrong one within seconds of the next request.
        """

        async def call() -> Entitlement:
            res = await request_async(my_entitlement, self._client, self._bound(timeout))
            return parse_body(unwrap(res), Entitlement.from_dict)

        return await self._retrying(call, self._retries if retries is None else retries)

    async def lookup_batch(
        self,
        ips: Iterable[str],
        *,
        concurrency: int | None = None,
        retries: int | None = None,
        timeout: float | None = None,
    ) -> dict[str, Result | VPNDetectionError]:
        """Classify many addresses in as few requests as possible.

        Bogons are answered locally and cached answers are reused; everything else goes
        to the batch endpoint in chunks of up to 1000 addresses, with at most
        `concurrency` chunks in flight. Keyed by address rather than positional, so
        duplicates in the input collapse to a single entry and the caller never has to
        line two lists up. An address that fails carries its error as its value, so one
        bad entry cannot lose the rest of the answers: the API reports a per-entry
        failure with the status the single lookup would have answered, and a chunk that
        fails as a whole marks every address in it.

        Each batch gets its own semaphore sized for THIS call, so a per-call concurrency
        really is the ceiling rather than being silently capped by the client's. A per-call
        `concurrency` below 1 is refused as `bad_request` before anything is sent.
        """
        check_concurrency(concurrency)
        check_timeout(timeout)
        unique = list(dict.fromkeys(ips))
        answers: dict[str, Result | VPNDetectionError] = {}
        pending: list[str] = []
        for ip in unique:
            if is_bogon(ip):
                answers[ip] = bogon_result(ip)
                continue
            hit = self._cache.get(ip) if self._cache is not None else None
            if hit is not None:
                answers[ip] = hit
                continue
            pending.append(ip)
        if pending:
            workers = self._concurrency if concurrency is None else concurrency
            gate = asyncio.Semaphore(max(1, workers))

            async def one(chunk: list[str]) -> dict[str, Result | VPNDetectionError]:
                async with gate:
                    return await self._lookup_chunk(chunk, retries, timeout)

            for chunk_answers in await asyncio.gather(
                *(one(chunk) for chunk in chunked(pending, BATCH_MAX))
            ):
                answers.update(chunk_answers)
        return {ip: answers[ip] for ip in unique}

    # One POST /batch, mapped back onto the addresses it was asked about. A chunk-level
    # failure - the call refused, the transport failing, the retries exhausted - becomes
    # every address's error, exactly as it would have been had each been looked up alone.
    async def _lookup_chunk(
        self, chunk: list[str], retries: int | None, timeout: float | None
    ) -> dict[str, Result | VPNDetectionError]:
        async def call() -> dict[str, Any]:
            res = await request_async(
                lookup_batch,
                self._client,
                self._bound(timeout),
                body=BatchLookupRequest(ips=list(chunk)),
            )
            return unwrap(res)

        try:
            body = await self._retrying(call, self._retries if retries is None else retries)
        except VPNDetectionError as err:
            return {ip: err for ip in chunk}
        answers = batch_answers(chunk, body)
        if self._cache is not None:
            for ip, answer in answers.items():
                if isinstance(answer, Result):
                    self._cache.put(ip, answer)
        return answers

    async def aclose(self) -> None:
        await self._client.get_async_httpx_client().aclose()
        await self._transfer.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    # A per-call timeout, checked, or the client's own when the call gave none.
    def _bound(self, timeout: float | None) -> float | None:
        return self._timeout if timeout is None else check_timeout(timeout)

    async def _retrying(self, call: Callable[[], Awaitable[T]], retries: int) -> T:
        attempt = 0
        while True:
            try:
                return await call()
            except (VPNDetectionError, httpx.HTTPError) as exc:
                err = as_error(exc)
                delay = retry_delay(err, attempt, retries)
                if delay is None:
                    raise err
                await asyncio.sleep(delay)
                attempt += 1


class AsyncDatabaseApi:
    """The licensed dataset downloads. Access is granted by contract, not self-serve.

    `list` is a method here, which shadows the builtin for everything else in the class
    body, so the return annotations name `builtins.list` explicitly.

    Every call here that asks the API a question takes `timeout`, in seconds, bounding
    each ATTEMPT of that call alone and overriding the client's. The two transfers take
    none and refuse one rather than ignoring it: a dataset runs to gigabytes and minutes,
    so any bound that suits a JSON call would abandon a healthy download.
    """

    def __init__(self, owner: AsyncVPNDetection) -> None:
        self._owner = owner

    async def list(self, *, timeout: float | None = None) -> builtins.list[Database]:
        """Every dataset your organization is licensed to download.

        `timeout` bounds each attempt at this call alone, in place of the client's.
        """

        async def call() -> builtins.list[Database]:
            res = await request_async(list_databases, self._client, self._bound(timeout))
            return parse_body(unwrap(res), databases_of)

        return await self._retrying(call)

    async def metadata(self, dataset_id: str, *, timeout: float | None = None) -> DatabaseMetadata:
        """What is inside one dataset: schema, samples, row count and sizes.

        `timeout` bounds each attempt at this call alone, in place of the client's.
        """

        async def call() -> DatabaseMetadata:
            res = await request_async(
                database_metadata, self._client, self._bound(timeout), id=dataset_id
            )
            return parse_body(unwrap(res), DatabaseMetadata.from_dict)

        return await self._retrying(call)

    async def checksums(
        self, dataset_id: str, format: Format, *, timeout: float | None = None
    ) -> dict[str, str]:
        """Every checksum published for one dataset file, keyed by algorithm.

        `timeout` bounds each attempt at this call alone, in place of the client's.
        """

        async def call() -> dict[str, str]:
            res = await request_async(
                database_checksum,
                self._client,
                self._bound(timeout),
                id=dataset_id,
                format_=DatabaseFormat(format),
            )
            return parse_body(unwrap(res), checksums_of)

        return await self._retrying(call)

    async def downloads(
        self, limit: int = DEFAULT_DOWNLOADS_LIMIT, *, timeout: float | None = None
    ) -> builtins.list[Download]:
        """Your organization's recent download attempts, newest first.

        `timeout` bounds each attempt at this call alone, in place of the client's.
        """

        async def call() -> builtins.list[Download]:
            res = await request_async(
                list_downloads, self._client, self._bound(timeout), limit=limit
            )
            return parse_body(unwrap(res), downloads_of)

        return await self._retrying(call)

    async def download_url(
        self, dataset_id: str, format: Format, *, timeout: float | None = None
    ) -> str:
        """The time-limited URL for one dataset file.

        The API answers `302` to object storage. The URL is returned rather than the
        bytes so the caller decides how to transfer a file that routinely runs to
        gigabytes; the link authorizes the START of a transfer, so one already running is
        not interrupted when it lapses.

        `timeout` bounds each attempt at MINTING the link, which is an ordinary API
        request, and says nothing about the transfer you then run with it.
        """

        async def call() -> str:
            res = await request_async(
                download_database,
                self._client,
                self._bound(timeout),
                id=dataset_id,
                format_=DatabaseFormat(format),
            )
            return redirect_location(res)

        return await self._retrying(call)

    async def download(self, dataset_id: str, format: Format, path: str | os.PathLike[str]) -> int:
        """Download one dataset file to `path`, and return the bytes written.

        The bytes are streamed straight to disk, so nothing larger than a chunk is ever
        held in memory whatever the dataset weighs. They land in a neighboring `.part`
        file that is moved into place only once the whole transfer has arrived, so a
        failure leaves neither a truncated file at `path` nor the `.part` behind, and an
        existing copy at `path` survives a refresh that fails.

        A failure DURING the transfer surfaces as it happened, an `httpx` error or an
        `OSError`, rather than as this library's error type: a reset socket and a full
        disk are different problems, and only one of them is ours.

        Each chunk is written from a worker thread. A gigabyte of blocking writes on the
        event loop would stall every other task in the process for the length of the
        transfer, which is the one thing an async caller cannot afford.
        """
        res = await self._open_transfer(dataset_id, format)
        try:
            loop = asyncio.get_running_loop()
            written = 0
            with part_file(path) as sink:
                async for chunk in res.aiter_bytes(TRANSFER_CHUNK_BYTES):
                    await loop.run_in_executor(None, sink.write, chunk)
                    written += len(chunk)
                # Inside, so a short transfer fails before anything is moved into place.
                assert_whole_transfer(res, written)
            return written
        finally:
            await res.aclose()

    async def download_bytes(self, dataset_id: str, format: Format) -> bytes:
        """Download one dataset file and hand back its bytes.

        **This holds the entire file in memory**, and the catalog spans five orders of
        magnitude, from `cdn_ip_v1` at 10 KB to `resproxy_ip_90d_v1` at 1.79 GB. Reach
        for it at the small end, where the bytes go straight into a parser, and use
        `download` for anything you have not measured.
        """
        res = await self._open_transfer(dataset_id, format)
        try:
            body = await res.aread()
            assert_whole_transfer(res, len(body))
            return body
        finally:
            await res.aclose()

    # Follows the 302 as a SECOND, unauthenticated request rather than by loosening the
    # redirect guard: the presigned URL authorizes itself, so forwarding the API key
    # would hand a credential to a host with no business holding it.
    #
    # Returns the response with its body still unread, so the caller decides whether a
    # dataset is going to disk or into memory.
    async def _open_transfer(self, dataset_id: str, format: Format) -> httpx.Response:
        url = await self.download_url(dataset_id, format)
        transfer = self._owner._transfer

        async def call() -> httpx.Response:
            res = await transfer.send(transfer.build_request("GET", url), stream=True)
            if res.status_code != httpx.codes.OK:
                await res.aclose()
                raise storage_refusal(res)
            return res

        return await self._retrying(call)

    @property
    def _client(self) -> AuthenticatedClient:
        return self._owner._client

    def _bound(self, timeout: float | None) -> float | None:
        return self._owner._bound(timeout)

    async def _retrying(self, call: Callable[[], Awaitable[T]]) -> T:
        return await self._owner._retrying(call, self._owner._retries)


class AsyncOauthApi:
    """`OauthApi`, for asyncio. Cancelling the task stops a poll's wait and any request in
    flight at once, and surfaces as `asyncio.CancelledError`."""

    def __init__(self, owner: AsyncVPNDetection) -> None:
        self._owner = owner
        self._clock = AsyncClock()

    async def metadata(self, *, timeout: float | None = None) -> OauthMetadata:
        """The authorization server's discovery document."""

        async def call() -> OauthMetadata:
            res = await self._send("GET", OAUTH_METADATA_PATH, None, timeout)
            return to_oauth_metadata(oauth_body(res), res.status_code)

        return await self._owner._retrying(call, self._owner._retries)

    async def device_authorization(
        self,
        client_id: str,
        *,
        scope: str | None = None,
        resource: str | None = None,
        timeout: float | None = None,
    ) -> DeviceAuthorization:
        """Start a device sign-in; see `OauthApi.device_authorization`."""
        form = {"client_id": client_id}
        if scope is not None:
            form["scope"] = scope
        if resource is not None:
            form["resource"] = resource

        async def call() -> DeviceAuthorization:
            res = await self._send("POST", OAUTH_DEVICE_AUTHORIZATION_PATH, form, timeout)
            return to_device_authorization(oauth_body(res), res.status_code)

        return await self._owner._retrying(call, self._owner._retries)

    async def exchange_device_code(
        self, client_id: str, device_code: str, *, timeout: float | None = None
    ) -> TokenResponse:
        """Redeem an approved device code, once; see `OauthApi.exchange_device_code`."""
        form = {"grant_type": DEVICE_CODE_GRANT, "device_code": device_code, "client_id": client_id}
        return await self._exchange(form, timeout)

    async def exchange_refresh_token(
        self, client_id: str, refresh_token: str, *, timeout: float | None = None
    ) -> TokenResponse:
        """Trade a refresh token for a new pair, once; see `OauthApi.exchange_refresh_token`."""
        form = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        }
        return await self._exchange(form, timeout)

    async def revoke(self, client_id: str, token: str, *, timeout: float | None = None) -> None:
        """End a token; revoking the refresh token signs the machine out."""

        async def call() -> None:
            form = {"token": token, "client_id": client_id}
            await self._send("POST", OAUTH_REVOKE_PATH, form, timeout)

        await self._owner._retrying(call, self._owner._retries)

    async def poll_device_token(
        self, client_id: str, device: DeviceAuthorization, *, timeout: float | None = None
    ) -> TokenResponse:
        """Wait for the person to approve a device sign-in; see `OauthApi.poll_device_token`.
        Cancel the task to stop waiting."""
        # Refused before the first wait, not after it.
        check_timeout(timeout)
        interval = device.interval if device.interval >= 1 else 5
        deadline = self._clock.now() + device.expires_in
        while True:
            await self._clock.sleep(interval)
            if self._clock.now() >= deadline:
                raise OauthExpiredTokenError()
            try:
                return await self.exchange_device_code(
                    client_id, device.device_code, timeout=timeout
                )
            except OauthError as err:
                # RFC 8628: slow_down widens the interval for every later request, not the next.
                if err.error_code == "slow_down":
                    interval += 5
                elif err.error_code != "authorization_pending":
                    raise

    async def _exchange(self, form: dict[str, str], timeout: float | None) -> TokenResponse:
        async def call() -> TokenResponse:
            res = await self._send("POST", OAUTH_TOKEN_PATH, form, timeout)
            return to_token_response(oauth_body(res), res.status_code)

        return await self._owner._retrying(call, 0)

    async def _send(
        self, method: str, path: str, form: dict[str, str] | None, timeout: float | None
    ) -> httpx.Response:
        bound = self._owner._bound(timeout)
        return await oauth_request_async(self._owner._client, method, path, form, bound)

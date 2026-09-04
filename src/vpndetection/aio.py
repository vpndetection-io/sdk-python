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
from typing import Self, TypeVar

import httpx

from ._core import (
    DEFAULT_BASE_URL,
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_CONCURRENCY,
    DEFAULT_DOWNLOADS_LIMIT,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    TRANSFER_CHUNK_BYTES,
    Cache,
    as_error,
    assert_whole_transfer,
    build_async_transfer_client,
    build_client,
    checksums_of,
    datasets_of,
    downloads_of,
    parse_body,
    part_file,
    redirect_location,
    retry_delay,
    send_async,
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
from ._generated.api.lookup import lookup_ip
from ._generated.client import AuthenticatedClient
from ._generated.models.database_checksum_format import DatabaseChecksumFormat
from ._generated.models.dataset_metadata import DatasetMetadata
from ._generated.models.download import Download
from ._generated.models.download_database_format import DownloadDatabaseFormat
from ._generated.models.licensed_dataset import LicensedDataset
from .bogon import bogon_result, is_bogon
from .errors import VPNDetectionError
from .models import Format, Result, to_result

__all__ = ["AsyncDatabaseApi", "AsyncVPNDetection"]

T = TypeVar("T")


class AsyncVPNDetection:
    """A client for the VPNDetection API, for asyncio.

    Identical in behavior to `VPNDetection`, including the per-instance cache and the
    bogon short-circuit. Close it with `await client.aclose()`, or use it as an async
    context manager.
    """

    database: AsyncDatabaseApi
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
        self._client = build_client(api_key, base_url, timeout, transport)
        self._transfer = build_async_transfer_client(timeout, transport)
        self._cache = Cache(cache_max_size, cache_ttl) if cache else None
        self._concurrency = concurrency
        self._retries = retries
        self.database = AsyncDatabaseApi(self)

    def is_bogon(self, ip: str) -> bool:
        """Whether an address is private, loopback, link-local, documentation, multicast
        or otherwise not routable, including the IPv6 equivalents and the 6to4 and
        Teredo ranges.

        Answered from a local table, so it is a plain function rather than a coroutine.
        """
        return is_bogon(ip)

    async def lookup(self, ip: str, *, retries: int | None = None) -> Result:
        """Classify one address.

        A bogon is answered locally and never reaches the network. Everything else is
        served, then cached for this instance.
        """
        if is_bogon(ip):
            return bogon_result(ip)
        if self._cache is not None:
            hit = self._cache.get(ip)
            if hit is not None:
                return hit

        async def call() -> Result:
            res = await send_async(lambda: lookup_ip.asyncio_detailed(ip, client=self._client))
            return parse_body(unwrap(res), to_result)

        result = await self._retrying(call, self._retries if retries is None else retries)
        if self._cache is not None:
            self._cache.put(ip, result)
        return result

    async def lookup_batch(
        self,
        ips: Iterable[str],
        *,
        concurrency: int | None = None,
        retries: int | None = None,
    ) -> dict[str, Result | VPNDetectionError]:
        """Classify many addresses concurrently.

        Keyed by address rather than positional, so duplicates in the input collapse to
        a single request and the caller never has to line two lists up. An address that
        fails carries its error as its value, so one bad entry cannot lose the rest of
        the answers.

        Each batch gets its own semaphore sized for THIS call, so a per-call concurrency
        really is the ceiling rather than being silently capped by the client's.
        """
        unique = list(dict.fromkeys(ips))
        if not unique:
            return {}
        workers = self._concurrency if concurrency is None else concurrency
        gate = asyncio.Semaphore(max(1, workers))

        async def one(ip: str) -> Result | VPNDetectionError:
            async with gate:
                try:
                    return await self.lookup(ip, retries=retries)
                except VPNDetectionError as err:
                    return err

        answers = await asyncio.gather(*(one(ip) for ip in unique))
        return dict(zip(unique, answers, strict=True))

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
    """

    def __init__(self, owner: AsyncVPNDetection) -> None:
        self._owner = owner

    async def list(self) -> builtins.list[LicensedDataset]:
        """Every dataset your organization is licensed to download."""

        async def call() -> builtins.list[LicensedDataset]:
            res = await send_async(lambda: list_databases.asyncio_detailed(client=self._client))
            return parse_body(unwrap(res), datasets_of)

        return await self._retrying(call)

    async def metadata(self, dataset_id: str) -> DatasetMetadata:
        """What is inside one dataset: schema, samples, row count and sizes."""

        async def call() -> DatasetMetadata:
            res = await send_async(
                lambda: database_metadata.asyncio_detailed(client=self._client, id=dataset_id)
            )
            return parse_body(unwrap(res), DatasetMetadata.from_dict)

        return await self._retrying(call)

    async def checksums(self, dataset_id: str, format: Format) -> dict[str, str]:
        """Every checksum published for one dataset file, keyed by algorithm."""

        async def call() -> dict[str, str]:
            res = await send_async(
                lambda: database_checksum.asyncio_detailed(
                    client=self._client, id=dataset_id, format_=DatabaseChecksumFormat(format)
                )
            )
            return parse_body(unwrap(res), checksums_of)

        return await self._retrying(call)

    async def downloads(self, limit: int = DEFAULT_DOWNLOADS_LIMIT) -> builtins.list[Download]:
        """Your organization's recent download attempts, newest first."""

        async def call() -> builtins.list[Download]:
            res = await send_async(
                lambda: list_downloads.asyncio_detailed(client=self._client, limit=limit)
            )
            return parse_body(unwrap(res), downloads_of)

        return await self._retrying(call)

    async def download_url(self, dataset_id: str, format: Format) -> str:
        """The time-limited URL for one dataset file.

        The API answers `302` to object storage. The URL is returned rather than the
        bytes so the caller decides how to transfer a file that routinely runs to
        gigabytes; the link authorizes the START of a transfer, so one already running is
        not interrupted when it lapses.
        """

        async def call() -> str:
            res = await send_async(
                lambda: download_database.asyncio_detailed(
                    client=self._client, id=dataset_id, format_=DownloadDatabaseFormat(format)
                )
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

    async def _retrying(self, call: Callable[[], Awaitable[T]]) -> T:
        return await self._owner._retrying(call, self._owner._retries)

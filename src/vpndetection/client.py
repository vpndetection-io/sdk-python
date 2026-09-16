"""The synchronous client."""

from __future__ import annotations

import builtins
import os
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
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
    TRANSFER_CHUNK_BYTES,
    Cache,
    as_error,
    assert_whole_transfer,
    batch_answers,
    build_client,
    build_transfer_client,
    checksums_of,
    chunked,
    databases_of,
    downloads_of,
    parse_body,
    part_file,
    redirect_location,
    request,
    retry_delay,
    send,
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
from .errors import VPNDetectionError
from .models import Format, Result, to_result

__all__ = ["DatabaseApi", "VPNDetection"]

T = TypeVar("T")


class VPNDetection:
    """A client for the VPNDetection API.

    No API key is needed to start: the free tier answers `ip` and `is_vpn` and allows
    1000 requests per day per source address.

    The cache is per instance, so an answer is never shared between two clients holding
    different API keys and therefore entitled to different fields.

    `timeout` is how long one attempt at a request may take, in seconds, so a call that is
    retried can take longer in total; a database transfer is exempt. `lookup`, `my_ip`,
    `my_entitlement` and `lookup_batch` also take `retries` and `timeout`, which override
    the client's for that call alone.

    Holds an HTTP connection pool, so use it as a context manager or call `close()` when
    you are done with it.
    """

    database: DatabaseApi
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
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = build_client(api_key, base_url, timeout, transport)
        self._transfer = build_transfer_client(timeout, transport)
        self._cache = Cache(cache_max_size, cache_ttl) if cache else None
        self._concurrency = concurrency
        self._retries = retries
        self.database = DatabaseApi(self)

    def is_bogon(self, ip: str) -> bool:
        """Whether an address is private, loopback, link-local, documentation, multicast
        or otherwise not routable, including the IPv6 equivalents and the 6to4 and
        Teredo ranges.

        These are the addresses `lookup` answers locally. Exposed here so the check is
        reachable from the client you already hold; the same function is also importable
        on its own.
        """
        return is_bogon(ip)

    def lookup(
        self, ip: str, *, retries: int | None = None, timeout: float | None = None
    ) -> Result:
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

        def call() -> Result:
            res = request(lookup_ip, self._client, timeout, ip=ip)
            return parse_body(unwrap(res), to_result)

        result = self._retrying(call, self._retries if retries is None else retries)
        if self._cache is not None:
            self._cache.put(ip, result)
        return result

    def my_ip(self, *, retries: int | None = None, timeout: float | None = None) -> Result:
        """Classify the address this client is calling from.

        The same answer `lookup` would give for that address, at the same cost against
        your allowance. The address is the one our edge observed, so a call made through
        a proxy or a VPN reports the exit it left through - usually the point of asking.

        Deliberately NOT cached. The cache is keyed by address, and which address this
        is IS the question: a machine that moves between networks would otherwise be
        told where it used to be.
        """

        def call() -> Result:
            res = request(lookup_my_ip, self._client, timeout)
            return parse_body(unwrap(res), to_result)

        return self._retrying(call, self._retries if retries is None else retries)

    def my_entitlement(
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

        def call() -> Entitlement:
            res = request(my_entitlement, self._client, timeout)
            return parse_body(unwrap(res), Entitlement.from_dict)

        return self._retrying(call, self._retries if retries is None else retries)

    def lookup_batch(
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

        Each batch gets its own thread pool sized for THIS call, so a per-call
        concurrency really is the ceiling rather than being silently capped by the
        client's.
        """
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
            with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
                futures = [
                    pool.submit(self._lookup_chunk, chunk, retries, timeout)
                    for chunk in chunked(pending, BATCH_MAX)
                ]
            for future in futures:
                answers.update(future.result())
        return {ip: answers[ip] for ip in unique}

    def close(self) -> None:
        self._client.get_httpx_client().close()
        self._transfer.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    # One POST /batch, mapped back onto the addresses it was asked about. A chunk-level
    # failure - the call refused, the transport failing, the retries exhausted - becomes
    # every address's error, exactly as it would have been had each been looked up alone.
    def _lookup_chunk(
        self, chunk: list[str], retries: int | None, timeout: float | None
    ) -> dict[str, Result | VPNDetectionError]:
        def call() -> dict[str, Any]:
            res = request(
                lookup_batch, self._client, timeout, body=BatchLookupRequest(ips=list(chunk))
            )
            return unwrap(res)

        try:
            body = self._retrying(call, self._retries if retries is None else retries)
        except VPNDetectionError as err:
            return {ip: err for ip in chunk}
        answers = batch_answers(chunk, body)
        if self._cache is not None:
            for ip, answer in answers.items():
                if isinstance(answer, Result):
                    self._cache.put(ip, answer)
        return answers

    def _retrying(self, call: Callable[[], T], retries: int) -> T:
        attempt = 0
        while True:
            try:
                return call()
            except (VPNDetectionError, httpx.HTTPError) as exc:
                err = as_error(exc)
                delay = retry_delay(err, attempt, retries)
                if delay is None:
                    raise err
                time.sleep(delay)
                attempt += 1


class DatabaseApi:
    """The licensed dataset downloads. Access is granted by contract, not self-serve.

    `list` is a method here, which shadows the builtin for everything else in the class
    body, so the return annotations name `builtins.list` explicitly.
    """

    def __init__(self, owner: VPNDetection) -> None:
        self._owner = owner

    def list(self) -> builtins.list[Database]:
        """Every dataset your organization is licensed to download."""

        def call() -> builtins.list[Database]:
            res = send(lambda: list_databases.sync_detailed(client=self._client))
            return parse_body(unwrap(res), databases_of)

        return self._retrying(call)

    def metadata(self, dataset_id: str) -> DatabaseMetadata:
        """What is inside one dataset: schema, samples, row count and sizes."""

        def call() -> DatabaseMetadata:
            res = send(lambda: database_metadata.sync_detailed(client=self._client, id=dataset_id))
            return parse_body(unwrap(res), DatabaseMetadata.from_dict)

        return self._retrying(call)

    def checksums(self, dataset_id: str, format: Format) -> dict[str, str]:
        """Every checksum published for one dataset file, keyed by algorithm.

        Keyed rather than one digest because the API publishes md5, sha1, sha256 and
        sha512 side by side and which of them you want is your verifier's business.
        """

        def call() -> dict[str, str]:
            res = send(
                lambda: database_checksum.sync_detailed(
                    client=self._client, id=dataset_id, format_=DatabaseFormat(format)
                )
            )
            return parse_body(unwrap(res), checksums_of)

        return self._retrying(call)

    def downloads(self, limit: int = DEFAULT_DOWNLOADS_LIMIT) -> builtins.list[Download]:
        """Your organization's recent download attempts, newest first."""

        def call() -> builtins.list[Download]:
            res = send(lambda: list_downloads.sync_detailed(client=self._client, limit=limit))
            return parse_body(unwrap(res), downloads_of)

        return self._retrying(call)

    def download_url(self, dataset_id: str, format: Format) -> str:
        """The time-limited URL for one dataset file.

        The API answers `302` to object storage. The URL is returned rather than the
        bytes so the caller decides how to transfer a file that routinely runs to
        gigabytes; the link authorizes the START of a transfer, so one already running is
        not interrupted when it lapses.
        """

        def call() -> str:
            res = send(
                lambda: download_database.sync_detailed(
                    client=self._client, id=dataset_id, format_=DatabaseFormat(format)
                )
            )
            return redirect_location(res)

        return self._retrying(call)

    def download(self, dataset_id: str, format: Format, path: str | os.PathLike[str]) -> int:
        """Download one dataset file to `path`, and return the bytes written.

        The bytes are streamed straight to disk, so nothing larger than a chunk is ever
        held in memory whatever the dataset weighs. They land in a neighboring `.part`
        file that is moved into place only once the whole transfer has arrived, so a
        failure leaves neither a truncated file at `path` nor the `.part` behind, and an
        existing copy at `path` survives a refresh that fails.

        A failure DURING the transfer surfaces as it happened, an `httpx` error or an
        `OSError`, rather than as this library's error type: a reset socket and a full
        disk are different problems, and only one of them is ours.
        """
        res = self._open_transfer(dataset_id, format)
        try:
            written = 0
            with part_file(path) as sink:
                for chunk in res.iter_bytes(TRANSFER_CHUNK_BYTES):
                    sink.write(chunk)
                    written += len(chunk)
                # Inside, so a short transfer fails before anything is moved into place.
                assert_whole_transfer(res, written)
            return written
        finally:
            res.close()

    def download_bytes(self, dataset_id: str, format: Format) -> bytes:
        """Download one dataset file and hand back its bytes.

        **This holds the entire file in memory**, and the catalog spans five orders of
        magnitude, from `cdn_ip_v1` at 10 KB to `resproxy_ip_90d_v1` at 1.79 GB. Reach
        for it at the small end, where the bytes go straight into a parser, and use
        `download` for anything you have not measured.
        """
        res = self._open_transfer(dataset_id, format)
        try:
            body = res.read()
            assert_whole_transfer(res, len(body))
            return body
        finally:
            res.close()

    # Follows the 302 as a SECOND, unauthenticated request rather than by loosening the
    # redirect guard: the presigned URL authorizes itself, so forwarding the API key
    # would hand a credential to a host with no business holding it.
    #
    # Returns the response with its body still unread, so the caller decides whether a
    # dataset is going to disk or into memory.
    def _open_transfer(self, dataset_id: str, format: Format) -> httpx.Response:
        url = self.download_url(dataset_id, format)
        transfer = self._owner._transfer

        def call() -> httpx.Response:
            res = transfer.send(transfer.build_request("GET", url), stream=True)
            if res.status_code != httpx.codes.OK:
                res.close()
                raise storage_refusal(res)
            return res

        return self._retrying(call)

    @property
    def _client(self) -> AuthenticatedClient:
        return self._owner._client

    def _retrying(self, call: Callable[[], T]) -> T:
        return self._owner._retrying(call, self._owner._retries)

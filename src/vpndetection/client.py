"""The synchronous client."""

from __future__ import annotations

import builtins
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
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
    Cache,
    as_error,
    build_client,
    checksums_of,
    datasets_of,
    downloads_of,
    parse_body,
    redirect_location,
    retry_delay,
    send,
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

__all__ = ["DatabaseApi", "VPNDetection"]

T = TypeVar("T")


class VPNDetection:
    """A client for the VPNDetection API.

    No API key is needed to start: the free tier answers `ip` and `is_vpn` and allows
    1000 requests per day per source address.

    The cache is per instance, so an answer is never shared between two clients holding
    different API keys and therefore entitled to different fields.

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

    def lookup(self, ip: str, *, retries: int | None = None) -> Result:
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
            res = send(lambda: lookup_ip.sync_detailed(ip, client=self._client))
            return parse_body(unwrap(res), to_result)

        result = self._retrying(call, self._retries if retries is None else retries)
        if self._cache is not None:
            self._cache.put(ip, result)
        return result

    def lookup_batch(
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

        Each batch gets its own thread pool sized for THIS call, so a per-call
        concurrency really is the ceiling rather than being silently capped by the
        client's.
        """
        unique = list(dict.fromkeys(ips))
        if not unique:
            return {}
        workers = self._concurrency if concurrency is None else concurrency
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            answers = {ip: pool.submit(self._lookup_or_error, ip, retries) for ip in unique}
        return {ip: answers[ip].result() for ip in unique}

    def close(self) -> None:
        self._client.get_httpx_client().close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def _lookup_or_error(self, ip: str, retries: int | None) -> Result | VPNDetectionError:
        try:
            return self.lookup(ip, retries=retries)
        except VPNDetectionError as err:
            return err

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

    def list(self) -> builtins.list[LicensedDataset]:
        """Every dataset your organization is licensed to download."""

        def call() -> builtins.list[LicensedDataset]:
            res = send(lambda: list_databases.sync_detailed(client=self._client))
            return parse_body(unwrap(res), datasets_of)

        return self._retrying(call)

    def metadata(self, dataset_id: str) -> DatasetMetadata:
        """What is inside one dataset: schema, samples, row count and sizes."""

        def call() -> DatasetMetadata:
            res = send(lambda: database_metadata.sync_detailed(client=self._client, id=dataset_id))
            return parse_body(unwrap(res), DatasetMetadata.from_dict)

        return self._retrying(call)

    def checksums(self, dataset_id: str, format: Format) -> dict[str, str]:
        """Every checksum published for one dataset file, keyed by algorithm.

        Keyed rather than one digest because the API publishes md5, sha1, sha256 and
        sha512 side by side and which of them you want is your verifier's business.
        """

        def call() -> dict[str, str]:
            res = send(
                lambda: database_checksum.sync_detailed(
                    client=self._client, id=dataset_id, format_=DatabaseChecksumFormat(format)
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
                    client=self._client, id=dataset_id, format_=DownloadDatabaseFormat(format)
                )
            )
            return redirect_location(res)

        return self._retrying(call)

    @property
    def _client(self) -> AuthenticatedClient:
        return self._owner._client

    def _retrying(self, call: Callable[[], T]) -> T:
        return self._owner._retrying(call, self._owner._retries)

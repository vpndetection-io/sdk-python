"""The licensed-download half, which only the max key can reach: it is the tier holding
dataset licenses, and `db.download` is a scope the other three keys do not carry.

The transfer is budgeted before it starts. `metadata` publishes a size per format, and
that size is checked against the ceiling below FIRST, so a mistaken dataset id can never
quietly pull one of the gigabyte datasets through CI.
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest
import staging
import tiers
from staging import Fact

from vpndetection import DatasetMetadata, Format, LicensedDataset, VPNDetection, VPNDetectionError

# The max organization licenses `cdn_ip` for redistribution, and at ~10 KB it is the only
# dataset small enough to move in CI.
DATASET_ID = "cdn_ip_v1"
FORMAT: Format = "csvgz"
# 8 MiB against a ~10 KB dataset. Three orders of magnitude of headroom, so tripping it
# means the suite is pointed somewhere unintended, which is exactly when a transfer must
# not go ahead.
CEILING = 8 << 20
# A real catalog id the max organization holds no license for.
UNLICENSED_ID = "hosting_ip_v1"

HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def test_the_licensed_catalog_answers_the_schema_the_client_was_generated_from() -> None:
    client, _ = max_client()
    try:
        datasets = client.database.list()
    finally:
        client.close()

    assert datasets, "the max organization licenses nothing"
    ids = []
    for dataset in datasets:
        assert dataset.base and dataset.name, (
            f"a licensed family carries no base or name: {dataset}"
        )
        assert dataset.standing in ("expired", "licensed", "unlicensed"), (
            f"{dataset.base} carries an undocumented standing {dataset.standing!r}"
        )
        assert dataset.redistribution in ("evaluation", "internal", "redistribute"), (
            f"{dataset.base} carries an undocumented right {dataset.redistribution!r}"
        )
        assert_no_undocumented_keys(dataset)
        # The point of the family shape: a license covers the family, and these are the
        # ids the download and checksum calls take. Before the spec was corrected this
        # list did not exist, so `list` could not tell a caller what to download.
        assert dataset.versions, f"{dataset.base} carries no versions"
        for version in dataset.versions:
            assert version.id, f"{dataset.base} has a version with no id"
            assert version.formats, f"{version.id} carries no formats"
            ids.append(version.id)
    print(f"==> licensed: {', '.join(ids)}")


def assert_no_undocumented_keys(dataset: LicensedDataset) -> None:
    """The keys the payload carried that the client has no home for.

    A typed decode cannot show these: an undocumented field disappears silently. The
    generated model keeps them, which is what makes `docsGroup` assertable at all - it is
    a docs-site slug and must not be published as API surface.
    """
    extra = set(dataset.additional_properties)
    assert extra == set(), f"{dataset.base} carries undocumented keys: {sorted(extra)}"


def test_a_dataset_the_organization_does_not_license_is_refused_cleanly() -> None:
    client, recorder = max_client()
    try:
        with pytest.raises(VPNDetectionError) as caught:
            client.database.download_url(UNLICENSED_ID, FORMAT)
    finally:
        client.close()

    err = caught.value
    assert err.kind == "forbidden", (
        f"kind = {err.kind!r}, want 'forbidden'. If {UNLICENSED_ID} is now licensed to "
        f"this organization, point this at one that is not"
    )
    assert err.status == 403
    assert err.retryable is False, "a license refusal is not worth retrying"
    # The API says which refusal this is (`{"rc": "NOT_LICENSED"}`). Falling back to the
    # status means the client never read the envelope.
    assert not err.message.startswith("request failed with status"), (
        f"message = {err.message!r}, which is the client fallback, so the body went unread"
    )
    assert len(recorder.facts) == 1, (
        f"issued {len(recorder.facts)} request(s), and a 4xx must not be retried"
    )


def test_download_streams_a_real_dataset_to_disk_intact() -> None:
    got = transferred()

    assert got.written > 0, "nothing was transferred"
    assert got.path.stat().st_size == got.written, (
        f"the file is {got.path.stat().st_size} bytes and the method reported {got.written}"
    )
    assert not Path(f"{got.path}.part").exists(), "the .part file outlived a successful transfer"
    body = got.path.read_bytes()
    assert body[:2] == b"\x1f\x8b", "the payload is not gzip"

    assert HEX_DIGEST.match(got.sha256), (
        f"sha256 = {got.sha256!r}, so the checksums did not unwrap past the envelope"
    )
    assert digest(body) == got.sha256, (
        f"the bytes hash to {digest(body)} and the API publishes {got.sha256}"
    )

    # The presigned URL authorizes itself, so the request that follows the 302 must carry
    # no credential.
    storage = [fact for fact in got.facts if fact.origin != staging.STAGING]
    assert storage, "nothing was fetched from object storage, so no 302 was followed"
    for fact in storage:
        assert not fact.carried_key, f"the API key was sent to object storage at {fact.origin}"


def test_download_bytes_agrees_with_the_streamed_copy() -> None:
    got = transferred()
    client, _ = max_client()
    try:
        raw = client.database.download_bytes(DATASET_ID, FORMAT)
    finally:
        client.close()

    assert len(raw) == got.written, (
        f"the in-memory copy is {len(raw)} bytes and the streamed one {got.written}"
    )
    assert digest(raw) == got.sha256


def test_the_async_client_downloads_the_same_bytes() -> None:
    got = transferred()
    if tiers.MAX.skip_reason():
        pytest.skip(tiers.MAX.skip_reason() or "")

    raw, facts = asyncio.run(async_download())

    assert digest(raw) == got.sha256, "the async client transferred something else"
    storage = [fact for fact in facts if fact.origin != staging.STAGING]
    assert storage, "the async client followed no 302"
    for fact in storage:
        assert not fact.carried_key, f"the async client sent the key to {fact.origin}"


async def async_download() -> tuple[bytes, list[Fact]]:
    client, recorder = staging.async_client_for(tiers.MAX)
    try:
        return await client.database.download_bytes(DATASET_ID, FORMAT), recorder.facts
    finally:
        await client.aclose()


def max_client() -> tuple[VPNDetection, staging.Recorder]:
    """A client of its own per test, so one test's request record cannot be read through
    another's."""
    reason = tiers.MAX.skip_reason()
    if reason:
        pytest.skip(reason)
    return staging.client_for(tiers.MAX)


@dataclass(frozen=True)
class Transfer:
    written: int
    path: Path
    sha256: str
    facts: list[Fact]


_transfer: Transfer | None = None


def transferred() -> Transfer:
    """The one real download this suite makes, memoized.

    Held in a directory of the module's own rather than a pytest `tmp_path`, which belongs
    to whichever test happened to ask first and would be gone before the others read it.
    """
    global _transfer
    if _transfer is not None:
        return _transfer

    client, recorder = max_client()
    try:
        meta = client.database.metadata(DATASET_ID)
        assert meta.id == DATASET_ID, f"metadata answered about {meta.id!r}, want {DATASET_ID!r}"
        size = published_size(meta)
        assert 0 < size <= CEILING, (
            f"{DATASET_ID} is {size} bytes, past the {CEILING} ceiling, so it is not transferred"
        )

        path = Path(tempfile.mkdtemp(prefix="vpndetection-integration-")) / f"{DATASET_ID}.csv.gz"
        written = client.database.download(DATASET_ID, FORMAT, path)
        # Read after the transfer, so a rebuild between the two calls shows up as a digest
        # mismatch rather than passing against a digest of nothing.
        checksums = client.database.checksums(DATASET_ID, FORMAT)
    finally:
        client.close()
    print(f"==> {DATASET_ID}.{FORMAT}: {written} bytes, metadata says {size}")

    _transfer = Transfer(
        written=written, path=path, sha256=checksums.get("sha256", ""), facts=recorder.facts
    )
    return _transfer


def published_size(meta: DatasetMetadata) -> int:
    sizes = getattr(meta.size, "additional_properties", None)
    assert sizes, f"{DATASET_ID} publishes no size to check a transfer against"
    assert FORMAT in sizes, f"{DATASET_ID} publishes no {FORMAT} size to check a transfer against"
    return int(sizes[FORMAT])


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.batch_lookup_request import BatchLookupRequest
from ...models.batch_lookup_response import BatchLookupResponse
from ...models.lookup_error import LookupError_
from ...types import Response


def _get_kwargs(
    *,
    body: BatchLookupRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/batch",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BatchLookupResponse | LookupError_ | None:
    if response.status_code == 200:
        response_200 = BatchLookupResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = LookupError_.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = LookupError_.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = LookupError_.from_dict(response.json())

        return response_403

    if response.status_code == 413:
        response_413 = LookupError_.from_dict(response.json())

        return response_413

    if response.status_code == 429:
        response_429 = LookupError_.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[BatchLookupResponse | LookupError_]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BatchLookupRequest,
) -> Response[BatchLookupResponse | LookupError_]:
    """Batch

     Answers up to 1000 addresses in one call. Each distinct string in `ips`
    is one lookup: it costs exactly what `GET /{ip}` costs for that address
    and comes back with exactly the fields that call would carry for your
    plan. Exact duplicates collapse to one entry and one lookup.

    Both maps in the answer are keyed by the string you sent, so nothing has
    to be lined up by position; the `ip` inside each result is the
    normalized form. An address that could not be answered sits in `errors`
    with the status and message the single lookup would have given, and
    never disturbs the others: a string that is not an address is a `400`
    there, and an allowance that runs out part way through leaves the
    remaining entries as `429`s.

    The call itself fails only for the reasons below, and a `429` on the
    call always carries `Retry-After`: the batch is admitted or refused
    whole by the rate limit, so a per-entry `429` is always a spent
    allowance and never a throttle.

    Args:
        body (BatchLookupRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BatchLookupResponse | LookupError_]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: BatchLookupRequest,
) -> BatchLookupResponse | LookupError_ | None:
    """Batch

     Answers up to 1000 addresses in one call. Each distinct string in `ips`
    is one lookup: it costs exactly what `GET /{ip}` costs for that address
    and comes back with exactly the fields that call would carry for your
    plan. Exact duplicates collapse to one entry and one lookup.

    Both maps in the answer are keyed by the string you sent, so nothing has
    to be lined up by position; the `ip` inside each result is the
    normalized form. An address that could not be answered sits in `errors`
    with the status and message the single lookup would have given, and
    never disturbs the others: a string that is not an address is a `400`
    there, and an allowance that runs out part way through leaves the
    remaining entries as `429`s.

    The call itself fails only for the reasons below, and a `429` on the
    call always carries `Retry-After`: the batch is admitted or refused
    whole by the rate limit, so a per-entry `429` is always a spent
    allowance and never a throttle.

    Args:
        body (BatchLookupRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BatchLookupResponse | LookupError_
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BatchLookupRequest,
) -> Response[BatchLookupResponse | LookupError_]:
    """Batch

     Answers up to 1000 addresses in one call. Each distinct string in `ips`
    is one lookup: it costs exactly what `GET /{ip}` costs for that address
    and comes back with exactly the fields that call would carry for your
    plan. Exact duplicates collapse to one entry and one lookup.

    Both maps in the answer are keyed by the string you sent, so nothing has
    to be lined up by position; the `ip` inside each result is the
    normalized form. An address that could not be answered sits in `errors`
    with the status and message the single lookup would have given, and
    never disturbs the others: a string that is not an address is a `400`
    there, and an allowance that runs out part way through leaves the
    remaining entries as `429`s.

    The call itself fails only for the reasons below, and a `429` on the
    call always carries `Retry-After`: the batch is admitted or refused
    whole by the rate limit, so a per-entry `429` is always a spent
    allowance and never a throttle.

    Args:
        body (BatchLookupRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BatchLookupResponse | LookupError_]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BatchLookupRequest,
) -> BatchLookupResponse | LookupError_ | None:
    """Batch

     Answers up to 1000 addresses in one call. Each distinct string in `ips`
    is one lookup: it costs exactly what `GET /{ip}` costs for that address
    and comes back with exactly the fields that call would carry for your
    plan. Exact duplicates collapse to one entry and one lookup.

    Both maps in the answer are keyed by the string you sent, so nothing has
    to be lined up by position; the `ip` inside each result is the
    normalized form. An address that could not be answered sits in `errors`
    with the status and message the single lookup would have given, and
    never disturbs the others: a string that is not an address is a `400`
    there, and an allowance that runs out part way through leaves the
    remaining entries as `429`s.

    The call itself fails only for the reasons below, and a `429` on the
    call always carries `Retry-After`: the batch is admitted or refused
    whole by the rate limit, so a per-entry `429` is always a spent
    allowance and never a throttle.

    Args:
        body (BatchLookupRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BatchLookupResponse | LookupError_
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

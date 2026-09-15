from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_rc import AccountRc
from ...models.apikey_list import ApikeyList
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/iam/apikeys",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountRc | ApikeyList | None:
    if response.status_code == 200:
        response_200 = ApikeyList.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AccountRc.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AccountRc.from_dict(response.json())

        return response_403

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AccountRc | ApikeyList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | ApikeyList]:
    """List

     Metadata only. A key's secret is never in a list - not here and not in
    the console - because a list is the response that ends up in logs,
    caches and support tickets.

    `retrievable` says whether the secret could still be read back at all.
    A key issued before this product stored secrets recoverably was never
    kept, so `reveal` will refuse it permanently; rotating produces one
    that can be read.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | ApikeyList]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> AccountRc | ApikeyList | None:
    """List

     Metadata only. A key's secret is never in a list - not here and not in
    the console - because a list is the response that ends up in logs,
    caches and support tickets.

    `retrievable` says whether the secret could still be read back at all.
    A key issued before this product stored secrets recoverably was never
    kept, so `reveal` will refuse it permanently; rotating produces one
    that can be read.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | ApikeyList
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | ApikeyList]:
    """List

     Metadata only. A key's secret is never in a list - not here and not in
    the console - because a list is the response that ends up in logs,
    caches and support tickets.

    `retrievable` says whether the secret could still be read back at all.
    A key issued before this product stored secrets recoverably was never
    kept, so `reveal` will refuse it permanently; rotating produces one
    that can be read.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | ApikeyList]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> AccountRc | ApikeyList | None:
    """List

     Metadata only. A key's secret is never in a list - not here and not in
    the console - because a list is the response that ends up in logs,
    caches and support tickets.

    `retrievable` says whether the secret could still be read back at all.
    A key issued before this product stored secrets recoverably was never
    kept, so `reveal` will refuse it permanently; rotating produces one
    that can be read.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | ApikeyList
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

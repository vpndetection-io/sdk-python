from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_error import AccountError
from ...models.account_me import AccountMe
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/account/me",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountError | AccountMe | None:
    if response.status_code == 200:
        response_200 = AccountMe.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AccountError.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AccountError.from_dict(response.json())

        return response_403

    if response.status_code == 503:
        response_503 = AccountError.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AccountError | AccountMe]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountError | AccountMe]:
    """Your key, plan and usage

     Answers what the presented key is, what plan is behind it, and what has
    been spent against that plan's allowance in the current window.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountError | AccountMe]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> AccountError | AccountMe | None:
    """Your key, plan and usage

     Answers what the presented key is, what plan is behind it, and what has
    been spent against that plan's allowance in the current window.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountError | AccountMe
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountError | AccountMe]:
    """Your key, plan and usage

     Answers what the presented key is, what plan is behind it, and what has
    been spent against that plan's allowance in the current window.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountError | AccountMe]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> AccountError | AccountMe | None:
    """Your key, plan and usage

     Answers what the presented key is, what plan is behind it, and what has
    been spent against that plan's allowance in the current window.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountError | AccountMe
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

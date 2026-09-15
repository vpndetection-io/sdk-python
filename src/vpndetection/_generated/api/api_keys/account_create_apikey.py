from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_create_apikey_request import AccountCreateApikeyRequest
from ...models.account_created_apikey import AccountCreatedApikey
from ...models.account_rc import AccountRc
from ...types import Response


def _get_kwargs(
    *,
    body: AccountCreateApikeyRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/iam/apikeys",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountCreatedApikey | AccountRc | None:
    if response.status_code == 200:
        response_200 = AccountCreatedApikey.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = AccountRc.from_dict(response.json())

        return response_400

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
) -> Response[AccountCreatedApikey | AccountRc]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: AccountCreateApikeyRequest,
) -> Response[AccountCreatedApikey | AccountRc]:
    """Create

     Creates a key and returns its secret.

    This is the ONLY response that ever carries the secret, and only
    because this is the moment it comes into existence. Store it now.

    Args:
        body (AccountCreateApikeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountCreatedApikey | AccountRc]
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
    body: AccountCreateApikeyRequest,
) -> AccountCreatedApikey | AccountRc | None:
    """Create

     Creates a key and returns its secret.

    This is the ONLY response that ever carries the secret, and only
    because this is the moment it comes into existence. Store it now.

    Args:
        body (AccountCreateApikeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountCreatedApikey | AccountRc
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: AccountCreateApikeyRequest,
) -> Response[AccountCreatedApikey | AccountRc]:
    """Create

     Creates a key and returns its secret.

    This is the ONLY response that ever carries the secret, and only
    because this is the moment it comes into existence. Store it now.

    Args:
        body (AccountCreateApikeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountCreatedApikey | AccountRc]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: AccountCreateApikeyRequest,
) -> AccountCreatedApikey | AccountRc | None:
    """Create

     Creates a key and returns its secret.

    This is the ONLY response that ever carries the secret, and only
    because this is the moment it comes into existence. Store it now.

    Args:
        body (AccountCreateApikeyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountCreatedApikey | AccountRc
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

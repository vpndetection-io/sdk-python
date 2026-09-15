from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_rc import AccountRc
from ...models.account_revealed_apikey import AccountRevealedApikey
from ...types import Response


def _get_kwargs(
    id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/account/apikeys/{id}/reveal".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountRc | AccountRevealedApikey | None:
    if response.status_code == 200:
        response_200 = AccountRevealedApikey.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = AccountRc.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = AccountRc.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = AccountRc.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[AccountRc | AccountRevealedApikey]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | AccountRevealedApikey]:
    """Read back a key's secret

     Returns an existing key's secret.

    Its own scope rather than part of `apikeys.manage`, because the two are
    different acts: rotating replaces a secret you never see, while this
    hands one over.

    Refused with `NOT_RETRIEVABLE` for a key issued before this product
    stored secrets recoverably - that secret was never kept, so no retry
    will ever produce it. Rotate the key instead.

    Args:
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | AccountRevealedApikey]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: AuthenticatedClient,
) -> AccountRc | AccountRevealedApikey | None:
    """Read back a key's secret

     Returns an existing key's secret.

    Its own scope rather than part of `apikeys.manage`, because the two are
    different acts: rotating replaces a secret you never see, while this
    hands one over.

    Refused with `NOT_RETRIEVABLE` for a key issued before this product
    stored secrets recoverably - that secret was never kept, so no retry
    will ever produce it. Rotate the key instead.

    Args:
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | AccountRevealedApikey
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | AccountRevealedApikey]:
    """Read back a key's secret

     Returns an existing key's secret.

    Its own scope rather than part of `apikeys.manage`, because the two are
    different acts: rotating replaces a secret you never see, while this
    hands one over.

    Refused with `NOT_RETRIEVABLE` for a key issued before this product
    stored secrets recoverably - that secret was never kept, so no retry
    will ever produce it. Rotate the key instead.

    Args:
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | AccountRevealedApikey]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: AuthenticatedClient,
) -> AccountRc | AccountRevealedApikey | None:
    """Read back a key's secret

     Returns an existing key's secret.

    Its own scope rather than part of `apikeys.manage`, because the two are
    different acts: rotating replaces a secret you never see, while this
    hands one over.

    Refused with `NOT_RETRIEVABLE` for a key issued before this product
    stored secrets recoverably - that secret was never kept, so no retry
    will ever produce it. Rotate the key instead.

    Args:
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | AccountRevealedApikey
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed

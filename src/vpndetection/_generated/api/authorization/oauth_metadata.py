from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_metadata import OauthMetadata
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/.well-known/oauth-authorization-server",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> OauthMetadata | None:
    if response.status_code == 200:
        response_200 = OauthMetadata.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[OauthMetadata]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[OauthMetadata]:
    """Discovery document

     RFC 8414 authorization server metadata: the endpoints, the grant types
    and the scopes this server supports.

    Read this rather than hardcoding endpoints. It is also served at
    `/.well-known/openid-configuration`, identically, because several
    clients probe that path first.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthMetadata]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> OauthMetadata | None:
    """Discovery document

     RFC 8414 authorization server metadata: the endpoints, the grant types
    and the scopes this server supports.

    Read this rather than hardcoding endpoints. It is also served at
    `/.well-known/openid-configuration`, identically, because several
    clients probe that path first.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthMetadata
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[OauthMetadata]:
    """Discovery document

     RFC 8414 authorization server metadata: the endpoints, the grant types
    and the scopes this server supports.

    Read this rather than hardcoding endpoints. It is also served at
    `/.well-known/openid-configuration`, identically, because several
    clients probe that path first.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthMetadata]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> OauthMetadata | None:
    """Discovery document

     RFC 8414 authorization server metadata: the endpoints, the grant types
    and the scopes this server supports.

    Read this rather than hardcoding endpoints. It is also served at
    `/.well-known/openid-configuration`, identically, because several
    clients probe that path first.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthMetadata
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

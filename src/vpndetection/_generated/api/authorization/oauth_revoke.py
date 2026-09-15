from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_revoke_response_200 import OauthRevokeResponse200
from ...models.revoke_request import RevokeRequest
from ...types import Response


def _get_kwargs(
    *,
    body: RevokeRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/revoke",
    }

    _kwargs["data"] = body.to_dict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> OauthRevokeResponse200 | None:
    if response.status_code == 200:
        response_200 = OauthRevokeResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[OauthRevokeResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RevokeRequest,
) -> Response[OauthRevokeResponse200]:
    """Revoke a token

     RFC 7009. Always answers 200, including for a token that was never
    valid - an endpoint that distinguished the two would be a way to test
    whether a stolen string is a live credential.

    Revoking a REFRESH token ends the whole authorization and takes its
    access tokens with it. Revoking an access token affects only that token.

    Args:
        body (RevokeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthRevokeResponse200]
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
    client: AuthenticatedClient | Client,
    body: RevokeRequest,
) -> OauthRevokeResponse200 | None:
    """Revoke a token

     RFC 7009. Always answers 200, including for a token that was never
    valid - an endpoint that distinguished the two would be a way to test
    whether a stolen string is a live credential.

    Revoking a REFRESH token ends the whole authorization and takes its
    access tokens with it. Revoking an access token affects only that token.

    Args:
        body (RevokeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthRevokeResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RevokeRequest,
) -> Response[OauthRevokeResponse200]:
    """Revoke a token

     RFC 7009. Always answers 200, including for a token that was never
    valid - an endpoint that distinguished the two would be a way to test
    whether a stolen string is a live credential.

    Revoking a REFRESH token ends the whole authorization and takes its
    access tokens with it. Revoking an access token affects only that token.

    Args:
        body (RevokeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthRevokeResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: RevokeRequest,
) -> OauthRevokeResponse200 | None:
    """Revoke a token

     RFC 7009. Always answers 200, including for a token that was never
    valid - an endpoint that distinguished the two would be a way to test
    whether a stolen string is a live credential.

    Revoking a REFRESH token ends the whole authorization and takes its
    access tokens with it. Revoking an access token affects only that token.

    Args:
        body (RevokeRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthRevokeResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

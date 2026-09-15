from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_error import OauthError
from ...models.token_request import TokenRequest
from ...models.token_response import TokenResponse
from ...types import Response


def _get_kwargs(
    *,
    body: TokenRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/token",
    }

    _kwargs["data"] = body.to_dict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> OauthError | TokenResponse | None:
    if response.status_code == 200:
        response_200 = TokenResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OauthError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[OauthError | TokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest,
) -> Response[OauthError | TokenResponse]:
    """Token

     Three grant types.

    `urn:ietf:params:oauth:grant-type:device_code` polls a device
    authorization. Until the person approves it answers
    `authorization_pending`; poll faster than `interval` and it answers
    `slow_down`, which means widen your interval and keep it widened.

    `authorization_code` exchanges a code from `/oauth/authorize`, with the
    `code_verifier` matching the challenge you sent.

    `refresh_token` exchanges a refresh token. The presented token is
    consumed whatever happens next, so store the new one before using it.

    Args:
        body (TokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthError | TokenResponse]
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
    body: TokenRequest,
) -> OauthError | TokenResponse | None:
    """Token

     Three grant types.

    `urn:ietf:params:oauth:grant-type:device_code` polls a device
    authorization. Until the person approves it answers
    `authorization_pending`; poll faster than `interval` and it answers
    `slow_down`, which means widen your interval and keep it widened.

    `authorization_code` exchanges a code from `/oauth/authorize`, with the
    `code_verifier` matching the challenge you sent.

    `refresh_token` exchanges a refresh token. The presented token is
    consumed whatever happens next, so store the new one before using it.

    Args:
        body (TokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthError | TokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest,
) -> Response[OauthError | TokenResponse]:
    """Token

     Three grant types.

    `urn:ietf:params:oauth:grant-type:device_code` polls a device
    authorization. Until the person approves it answers
    `authorization_pending`; poll faster than `interval` and it answers
    `slow_down`, which means widen your interval and keep it widened.

    `authorization_code` exchanges a code from `/oauth/authorize`, with the
    `code_verifier` matching the challenge you sent.

    `refresh_token` exchanges a refresh token. The presented token is
    consumed whatever happens next, so store the new one before using it.

    Args:
        body (TokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[OauthError | TokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: TokenRequest,
) -> OauthError | TokenResponse | None:
    """Token

     Three grant types.

    `urn:ietf:params:oauth:grant-type:device_code` polls a device
    authorization. Until the person approves it answers
    `authorization_pending`; poll faster than `interval` and it answers
    `slow_down`, which means widen your interval and keep it widened.

    `authorization_code` exchanges a code from `/oauth/authorize`, with the
    `code_verifier` matching the challenge you sent.

    `refresh_token` exchanges a refresh token. The presented token is
    consumed whatever happens next, so store the new one before using it.

    Args:
        body (TokenRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        OauthError | TokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

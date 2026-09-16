from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_authorization import DeviceAuthorization
from ...models.device_authorization_request import DeviceAuthorizationRequest
from ...models.oauth_error import OauthError
from ...types import Response


def _get_kwargs(
    *,
    body: DeviceAuthorizationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/device_authorization",
    }

    _kwargs["data"] = body.to_dict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeviceAuthorization | OauthError | None:
    if response.status_code == 200:
        response_200 = DeviceAuthorization.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = OauthError.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = OauthError.from_dict(response.json())

        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeviceAuthorization | OauthError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceAuthorizationRequest,
) -> Response[DeviceAuthorization | OauthError]:
    """Device authorization

     Starts the device flow. Show the `user_code` to the person and send them
    to `verification_uri`; `verification_uri_complete` has the code already
    embedded, which is what to open if you can open a browser at all.

    Then poll `/oauth/token`, no faster than `interval` seconds.

    Args:
        body (DeviceAuthorizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAuthorization | OauthError]
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
    body: DeviceAuthorizationRequest,
) -> DeviceAuthorization | OauthError | None:
    """Device authorization

     Starts the device flow. Show the `user_code` to the person and send them
    to `verification_uri`; `verification_uri_complete` has the code already
    embedded, which is what to open if you can open a browser at all.

    Then poll `/oauth/token`, no faster than `interval` seconds.

    Args:
        body (DeviceAuthorizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAuthorization | OauthError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceAuthorizationRequest,
) -> Response[DeviceAuthorization | OauthError]:
    """Device authorization

     Starts the device flow. Show the `user_code` to the person and send them
    to `verification_uri`; `verification_uri_complete` has the code already
    embedded, which is what to open if you can open a browser at all.

    Then poll `/oauth/token`, no faster than `interval` seconds.

    Args:
        body (DeviceAuthorizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceAuthorization | OauthError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: DeviceAuthorizationRequest,
) -> DeviceAuthorization | OauthError | None:
    """Device authorization

     Starts the device flow. Show the `user_code` to the person and send them
    to `verification_uri`; `verification_uri_complete` has the code already
    embedded, which is what to open if you can open a browser at all.

    Then poll `/oauth/token`, no faster than `interval` seconds.

    Args:
        body (DeviceAuthorizationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceAuthorization | OauthError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

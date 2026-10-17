from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.client_registration import ClientRegistration
from ...models.client_registration_request import ClientRegistrationRequest
from ...models.oauth_error import OauthError
from ...types import Response


def _get_kwargs(
    *,
    body: ClientRegistrationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/oauth/register",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ClientRegistration | OauthError | None:
    if response.status_code == 201:
        response_201 = ClientRegistration.from_dict(response.json())

        return response_201

    if response.status_code == 400:
        response_400 = OauthError.from_dict(response.json())

        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ClientRegistration | OauthError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ClientRegistrationRequest,
) -> Response[ClientRegistration | OauthError]:
    """Register

     RFC 7591 dynamic client registration, for a client that cannot use a
    Client ID Metadata Document. Post your client's metadata as JSON, then
    use the `client_id` in the answer at `/oauth/authorize` and
    `/oauth/token`. Nothing is kept until a person approves your client, so
    registering again costs nothing and leaves nothing to clean up.

    Each redirect URI must be https on a public host name, or http on a
    loopback address (`127.0.0.1`, `[::1]`, `localhost`), which then
    matches on any port. A custom URI scheme is refused: use a loopback
    redirect instead. So is a host on one of our own domains.

    `client_name` is shown to the person as your client's own claim, with
    where its redirect goes beside it. A name that renders blank, or mixes
    Latin letters with Cyrillic or Greek ones, is shown as an unnamed
    application.

    The client is public whatever you ask for: `token_endpoint_auth_method`
    comes back `none`, there is no client secret, and every authorization
    proves itself with PKCE. It may be granted `apikeys.use` at most.

    Args:
        body (ClientRegistrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientRegistration | OauthError]
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
    body: ClientRegistrationRequest,
) -> ClientRegistration | OauthError | None:
    """Register

     RFC 7591 dynamic client registration, for a client that cannot use a
    Client ID Metadata Document. Post your client's metadata as JSON, then
    use the `client_id` in the answer at `/oauth/authorize` and
    `/oauth/token`. Nothing is kept until a person approves your client, so
    registering again costs nothing and leaves nothing to clean up.

    Each redirect URI must be https on a public host name, or http on a
    loopback address (`127.0.0.1`, `[::1]`, `localhost`), which then
    matches on any port. A custom URI scheme is refused: use a loopback
    redirect instead. So is a host on one of our own domains.

    `client_name` is shown to the person as your client's own claim, with
    where its redirect goes beside it. A name that renders blank, or mixes
    Latin letters with Cyrillic or Greek ones, is shown as an unnamed
    application.

    The client is public whatever you ask for: `token_endpoint_auth_method`
    comes back `none`, there is no client secret, and every authorization
    proves itself with PKCE. It may be granted `apikeys.use` at most.

    Args:
        body (ClientRegistrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientRegistration | OauthError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: ClientRegistrationRequest,
) -> Response[ClientRegistration | OauthError]:
    """Register

     RFC 7591 dynamic client registration, for a client that cannot use a
    Client ID Metadata Document. Post your client's metadata as JSON, then
    use the `client_id` in the answer at `/oauth/authorize` and
    `/oauth/token`. Nothing is kept until a person approves your client, so
    registering again costs nothing and leaves nothing to clean up.

    Each redirect URI must be https on a public host name, or http on a
    loopback address (`127.0.0.1`, `[::1]`, `localhost`), which then
    matches on any port. A custom URI scheme is refused: use a loopback
    redirect instead. So is a host on one of our own domains.

    `client_name` is shown to the person as your client's own claim, with
    where its redirect goes beside it. A name that renders blank, or mixes
    Latin letters with Cyrillic or Greek ones, is shown as an unnamed
    application.

    The client is public whatever you ask for: `token_endpoint_auth_method`
    comes back `none`, there is no client secret, and every authorization
    proves itself with PKCE. It may be granted `apikeys.use` at most.

    Args:
        body (ClientRegistrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ClientRegistration | OauthError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: ClientRegistrationRequest,
) -> ClientRegistration | OauthError | None:
    """Register

     RFC 7591 dynamic client registration, for a client that cannot use a
    Client ID Metadata Document. Post your client's metadata as JSON, then
    use the `client_id` in the answer at `/oauth/authorize` and
    `/oauth/token`. Nothing is kept until a person approves your client, so
    registering again costs nothing and leaves nothing to clean up.

    Each redirect URI must be https on a public host name, or http on a
    loopback address (`127.0.0.1`, `[::1]`, `localhost`), which then
    matches on any port. A custom URI scheme is refused: use a loopback
    redirect instead. So is a host on one of our own domains.

    `client_name` is shown to the person as your client's own claim, with
    where its redirect goes beside it. A name that renders blank, or mixes
    Latin letters with Cyrillic or Greek ones, is shown as an unnamed
    application.

    The client is public whatever you ask for: `token_endpoint_auth_method`
    comes back `none`, there is no client secret, and every authorization
    proves itself with PKCE. It may be granted `apikeys.use` at most.

    Args:
        body (ClientRegistrationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ClientRegistration | OauthError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed

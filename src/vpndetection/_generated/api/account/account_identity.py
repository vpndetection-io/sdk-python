from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_rc import AccountRc
from ...models.identity import Identity
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/account/identity",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountRc | Identity | None:
    if response.status_code == 200:
        response_200 = Identity.from_dict(response.json())

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
) -> Response[AccountRc | Identity]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | Identity]:
    """Identity - who this credential belongs to

     The identity behind this credential: what it is, the organization it is
    scoped to, and the scopes it currently holds.

    `user` is present for an OAuth token and ABSENT for an API key, which
    has an organization but no person behind it. `credential.kind` says
    which you are holding, so a client can branch without guessing from a
    missing field.

    Narrower than what the console shows its own user on purpose: an
    integration needs a name to display and an organization to address, not
    a profile. The `scopes` array is what the credential may do RIGHT NOW,
    so a client can render its own capabilities rather than discovering
    them from a 403.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | Identity]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> AccountRc | Identity | None:
    """Identity - who this credential belongs to

     The identity behind this credential: what it is, the organization it is
    scoped to, and the scopes it currently holds.

    `user` is present for an OAuth token and ABSENT for an API key, which
    has an organization but no person behind it. `credential.kind` says
    which you are holding, so a client can branch without guessing from a
    missing field.

    Narrower than what the console shows its own user on purpose: an
    integration needs a name to display and an organization to address, not
    a profile. The `scopes` array is what the credential may do RIGHT NOW,
    so a client can render its own capabilities rather than discovering
    them from a 403.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | Identity
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountRc | Identity]:
    """Identity - who this credential belongs to

     The identity behind this credential: what it is, the organization it is
    scoped to, and the scopes it currently holds.

    `user` is present for an OAuth token and ABSENT for an API key, which
    has an organization but no person behind it. `credential.kind` says
    which you are holding, so a client can branch without guessing from a
    missing field.

    Narrower than what the console shows its own user on purpose: an
    integration needs a name to display and an organization to address, not
    a profile. The `scopes` array is what the credential may do RIGHT NOW,
    so a client can render its own capabilities rather than discovering
    them from a 403.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountRc | Identity]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> AccountRc | Identity | None:
    """Identity - who this credential belongs to

     The identity behind this credential: what it is, the organization it is
    scoped to, and the scopes it currently holds.

    `user` is present for an OAuth token and ABSENT for an API key, which
    has an organization but no person behind it. `credential.kind` says
    which you are holding, so a client can branch without guessing from a
    missing field.

    Narrower than what the console shows its own user on purpose: an
    integration needs a name to display and an organization to address, not
    a profile. The `scopes` array is what the credential may do RIGHT NOW,
    so a client can render its own capabilities rather than discovering
    them from a 403.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountRc | Identity
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

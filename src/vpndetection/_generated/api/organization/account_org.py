from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_org_wrap import AccountOrgWrap
from ...models.account_rc import AccountRc
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/iam/org",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccountOrgWrap | AccountRc | None:
    if response.status_code == 200:
        response_200 = AccountOrgWrap.from_dict(response.json())

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
) -> Response[AccountOrgWrap | AccountRc]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountOrgWrap | AccountRc]:
    """Organization

     The organization this credential is scoped to.

    There is no way to name a different one. A credential describes exactly
    one organization, so an identifier in the path could only ever be your
    own or a refusal.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountOrgWrap | AccountRc]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
) -> AccountOrgWrap | AccountRc | None:
    """Organization

     The organization this credential is scoped to.

    There is no way to name a different one. A credential describes exactly
    one organization, so an identifier in the path could only ever be your
    own or a refusal.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountOrgWrap | AccountRc
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
) -> Response[AccountOrgWrap | AccountRc]:
    """Organization

     The organization this credential is scoped to.

    There is no way to name a different one. A credential describes exactly
    one organization, so an identifier in the path could only ever be your
    own or a refusal.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountOrgWrap | AccountRc]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
) -> AccountOrgWrap | AccountRc | None:
    """Organization

     The organization this credential is scoped to.

    There is no way to name a different one. A credential describes exactly
    one organization, so an identifier in the path could only ever be your
    own or a refusal.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountOrgWrap | AccountRc
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed

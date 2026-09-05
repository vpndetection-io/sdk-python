from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.lookup_error import LookupError_
from ...models.lookup_response import LookupResponse
from ...types import Response


def _get_kwargs(
    ip: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{ip}".format(
            ip=quote(str(ip), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LookupError_ | LookupResponse | None:
    if response.status_code == 200:
        response_200 = LookupResponse.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = LookupError_.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = LookupError_.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = LookupError_.from_dict(response.json())

        return response_403

    if response.status_code == 429:
        response_429 = LookupError_.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = LookupError_.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[LookupError_ | LookupResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ip: str,
    *,
    client: AuthenticatedClient,
) -> Response[LookupError_ | LookupResponse]:
    """Lookup

     Answers what is known about a single IPv4 or IPv6 address. Which fields
    come back is decided by the plan behind the presented key; with no key
    the answer is `ip` and `is_vpn`.

    Args:
        ip (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LookupError_ | LookupResponse]
    """

    kwargs = _get_kwargs(
        ip=ip,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    ip: str,
    *,
    client: AuthenticatedClient,
) -> LookupError_ | LookupResponse | None:
    """Lookup

     Answers what is known about a single IPv4 or IPv6 address. Which fields
    come back is decided by the plan behind the presented key; with no key
    the answer is `ip` and `is_vpn`.

    Args:
        ip (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LookupError_ | LookupResponse
    """

    return sync_detailed(
        ip=ip,
        client=client,
    ).parsed


async def asyncio_detailed(
    ip: str,
    *,
    client: AuthenticatedClient,
) -> Response[LookupError_ | LookupResponse]:
    """Lookup

     Answers what is known about a single IPv4 or IPv6 address. Which fields
    come back is decided by the plan behind the presented key; with no key
    the answer is `ip` and `is_vpn`.

    Args:
        ip (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LookupError_ | LookupResponse]
    """

    kwargs = _get_kwargs(
        ip=ip,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ip: str,
    *,
    client: AuthenticatedClient,
) -> LookupError_ | LookupResponse | None:
    """Lookup

     Answers what is known about a single IPv4 or IPv6 address. Which fields
    come back is decided by the plan behind the presented key; with no key
    the answer is `ip` and `is_vpn`.

    Args:
        ip (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LookupError_ | LookupResponse
    """

    return (
        await asyncio_detailed(
            ip=ip,
            client=client,
        )
    ).parsed

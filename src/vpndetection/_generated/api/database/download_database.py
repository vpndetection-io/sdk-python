from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.download_database_format import DownloadDatabaseFormat
from ...models.error import Error
from ...types import UNSET, Response


def _get_kwargs(
    *,
    id: str,
    format_: DownloadDatabaseFormat,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["id"] = id

    json_format_ = format_.value
    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/database/download",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | Error | None:
    if response.status_code == 302:
        response_302 = cast(Any, None)
        return response_302

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    id: str,
    format_: DownloadDatabaseFormat,
) -> Response[Any | Error]:
    """Download

     Answers `302` with a time-limited URL pointing straight at object storage. Follow the redirect; the
    link authorizes the START of a transfer, so one already running is not interrupted when it lapses.

    Args:
        id (str):
        format_ (DownloadDatabaseFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        format_=format_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    id: str,
    format_: DownloadDatabaseFormat,
) -> Any | Error | None:
    """Download

     Answers `302` with a time-limited URL pointing straight at object storage. Follow the redirect; the
    link authorizes the START of a transfer, so one already running is not interrupted when it lapses.

    Args:
        id (str):
        format_ (DownloadDatabaseFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return sync_detailed(
        client=client,
        id=id,
        format_=format_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    id: str,
    format_: DownloadDatabaseFormat,
) -> Response[Any | Error]:
    """Download

     Answers `302` with a time-limited URL pointing straight at object storage. Follow the redirect; the
    link authorizes the START of a transfer, so one already running is not interrupted when it lapses.

    Args:
        id (str):
        format_ (DownloadDatabaseFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Error]
    """

    kwargs = _get_kwargs(
        id=id,
        format_=format_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    id: str,
    format_: DownloadDatabaseFormat,
) -> Any | Error | None:
    """Download

     Answers `302` with a time-limited URL pointing straight at object storage. Follow the redirect; the
    link authorizes the START of a transfer, so one already running is not interrupted when it lapses.

    Args:
        id (str):
        format_ (DownloadDatabaseFormat):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Error
    """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            format_=format_,
        )
    ).parsed

from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.oauth_authorize_code_challenge_method import OauthAuthorizeCodeChallengeMethod
from ...models.oauth_authorize_response_type import OauthAuthorizeResponseType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client_id: str,
    redirect_uri: str,
    response_type: OauthAuthorizeResponseType,
    code_challenge: str,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    resource: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["redirect_uri"] = redirect_uri

    json_response_type = response_type.value
    params["response_type"] = json_response_type

    params["code_challenge"] = code_challenge

    json_code_challenge_method: str | Unset = UNSET
    if not isinstance(code_challenge_method, Unset):
        json_code_challenge_method = code_challenge_method.value

    params["code_challenge_method"] = json_code_challenge_method

    params["scope"] = scope

    params["state"] = state

    params["resource"] = resource

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oauth/authorize",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 302:
        return None

    if response.status_code == 400:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str,
    response_type: OauthAuthorizeResponseType,
    code_challenge: str,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    resource: str | Unset = UNSET,
) -> Response[Any]:
    """Send a user here to approve

     The browser entry point for the authorization-code flow. This is a
    redirect target, not something to call from code.

    An unknown `client_id` or an unregistered `redirect_uri` is shown to the
    USER and never redirected, because sending an error to an address we
    have not verified belongs to you is how an open redirector works.
    Everything else comes back to your `redirect_uri` with `error`, your
    `state`, and `iss`.

    Args:
        client_id (str):
        redirect_uri (str):
        response_type (OauthAuthorizeResponseType):
        code_challenge (str):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):
        scope (str | Unset):
        state (str | Unset):
        resource (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        scope=scope,
        state=state,
        resource=resource,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    client_id: str,
    redirect_uri: str,
    response_type: OauthAuthorizeResponseType,
    code_challenge: str,
    code_challenge_method: OauthAuthorizeCodeChallengeMethod | Unset = UNSET,
    scope: str | Unset = UNSET,
    state: str | Unset = UNSET,
    resource: str | Unset = UNSET,
) -> Response[Any]:
    """Send a user here to approve

     The browser entry point for the authorization-code flow. This is a
    redirect target, not something to call from code.

    An unknown `client_id` or an unregistered `redirect_uri` is shown to the
    USER and never redirected, because sending an error to an address we
    have not verified belongs to you is how an open redirector works.
    Everything else comes back to your `redirect_uri` with `error`, your
    `state`, and `iss`.

    Args:
        client_id (str):
        redirect_uri (str):
        response_type (OauthAuthorizeResponseType):
        code_challenge (str):
        code_challenge_method (OauthAuthorizeCodeChallengeMethod | Unset):
        scope (str | Unset):
        state (str | Unset):
        resource (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        scope=scope,
        state=state,
        resource=resource,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)

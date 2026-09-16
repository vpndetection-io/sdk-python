"""The published package's `oauth` accessor against staging's authorization server.

Keyless, and only what is safe to repeat. The one device authorization is the most a run
may start: staging allows 30 a minute per source address, and every SDK's suite shares
that address. Nothing is ever polled, because nobody approves the sign-in.
"""

from __future__ import annotations

import importlib.metadata

import pytest
from staging import PACKAGE, STAGING

from vpndetection import VPNDetection

# The only client staging has registered, already public in the CLI's source.
CLIENT_ID = "vpndetection-cli"

# The first release with the accessor. Gated on the installed version rather than on the
# attribute, which would also skip quietly if the accessor were ever removed.
OAUTH_SINCE = (5, 2)

pytestmark = pytest.mark.skipif(
    tuple(int(part) for part in importlib.metadata.version(PACKAGE).split(".")[:2]) < OAUTH_SINCE,
    reason=f"the installed {PACKAGE} predates the oauth accessor",
)


def test_metadata_names_staging_as_the_issuer() -> None:
    with VPNDetection(base_url=STAGING) as client:
        metadata = client.oauth.metadata()

    assert metadata.issuer == STAGING
    assert metadata.device_authorization_endpoint
    assert "S256" in (metadata.code_challenge_methods_supported or ())


def test_revoking_a_token_that_never_existed_succeeds() -> None:
    with VPNDetection(base_url=STAGING) as client:
        client.oauth.revoke(CLIENT_ID, "mo_rt_sdk-ci-not-a-token")


def test_redeeming_an_unknown_device_code_is_the_expired_token_refusal() -> None:
    from vpndetection import OauthExpiredTokenError

    with VPNDetection(base_url=STAGING) as client, pytest.raises(OauthExpiredTokenError) as caught:
        client.oauth.exchange_device_code(CLIENT_ID, "mo_dc_sdk-ci-not-a-code")

    assert caught.value.status == 400


def test_a_device_authorization_starts_or_is_asked_to_slow_down() -> None:
    from vpndetection import OauthError

    with VPNDetection(base_url=STAGING, retries=0) as client:
        try:
            device = client.oauth.device_authorization(CLIENT_ID, scope="account.read")
        except OauthError as err:
            assert err.error_code == "slow_down", err
            return

    assert device.device_code
    assert device.user_code
    assert device.verification_uri.endswith("/device")
    assert device.expires_in > 0
    assert device.interval > 0

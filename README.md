# [<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" width="24"/>](https://vpndetection.io/) VPNDetection Python Client Library

[![PyPI](https://img.shields.io/pypi/v/vpndetection.svg)](https://pypi.org/project/vpndetection/)
[![license](https://img.shields.io/pypi/l/vpndetection.svg)](LICENSE)

The official Python client library for the [VPNDetection](https://vpndetection.io) API.

The library helps you query VPNDetection's APIs for anonymity detection including VPNs, residential proxies, Tor nodes, hosting servers, CDNs, relays and more.

## Getting Started

```bash
pip install vpndetection
```

Requires Python 3.11 or newer. Type hints are included, and the package ships `py.typed`.

## Usage

**No API key needed to start.** The free tier answers `ip` and `is_vpn`, and allows 1000 requests per day per source address.

```python
from vpndetection import VPNDetection

client = VPNDetection()

result = client.lookup("45.83.91.1")
print(result.is_vpn)   # True
```

The client holds an HTTP connection pool, so use it as a context manager, or call `client.close()` when you are done with it:

```python
with VPNDetection() as client:
    print(client.lookup("45.83.91.1").is_vpn)
```

### With an API key

An API key raises your quota, and raises your features on a paid plan. Create one in the [console](https://app.vpndetection.io), then pass it in:

```python
import os

client = VPNDetection(os.environ["VPNDETECTION_API_KEY"])

result = client.lookup("45.83.91.1")
print(result.is_vpn)          # True
print(result.vpn.provider)    # 'mullvad'
print(result.is_hosting)      # True
print(result.hosting.provider)
```

### Async

Everything above works the same way under asyncio, with `AsyncVPNDetection`:

```python
import asyncio
from vpndetection import AsyncVPNDetection

async def main():
    async with AsyncVPNDetection() as client:
        result = await client.lookup("45.83.91.1")
        print(result.is_vpn)   # True

asyncio.run(main())
```

### Your own address

```python
result = client.my_ip()
print(result.ip)   # the address we saw this call come from
```

Same answer `lookup` would give for that address, and the same cost against your allowance. It is deliberately not cached: which address you are is the whole question, and a machine that moves between networks would otherwise be told where it used to be.

### Your plan and usage

```python
acct = client.my_entitlement()
print(acct.plan.key)          # max
print(acct.usage.requests)    # 580
print(acct.usage.window_end)  # when the allowance resets
```

Usage counts against the anniversary of your subscription, not the calendar month and not the billing period, and it is the same number a lookup is gated on. `hard_limit` is `None` on an uncapped plan, which is not the same as zero.

Both are on the async client too: `await client.my_ip()` and `await client.my_entitlement()`.

### Batch lookup

Look up as many addresses as you like at once. Bogons and cached answers are handled locally, and everything else goes to the batch endpoint in chunks of up to 1000 addresses, in parallel:

```python
results = client.lookup_batch(["45.83.91.1", "8.8.8.8", "1.1.1.1"])

for ip, result in results.items():
    if isinstance(result, Exception):
        print(f"{ip}: {result}")
        continue
    print(f"{ip}: {result.is_vpn}")
```

Results are keyed by address, in the order you first listed each one, so duplicates in your list collapse into a single entry and one address failing never loses the rest: it carries its error as its value, with the status the API would have given that address on its own.

How many chunks are in flight at once, how many times a failed chunk is retried and how long each request may take are configurable per call:

```python
results = client.lookup_batch(many_ips, concurrency=4, retries=4, timeout=30)
```

### Caching

Answers are cached by default, so repeat lookups of the same address are free:

```python
client = VPNDetection()

result = client.lookup("45.83.91.1")
print(result.is_vpn)    # True, API request

result2 = client.lookup("45.83.91.1")
print(result2.is_vpn)   # True, no API request, result was cached
```

You can change the default cache variables (max size, TTL in seconds, etc) on initialization, or even disable it:

```python
client = VPNDetection(cache_max_size=50_000, cache_ttl=6 * 60 * 60)
client_no_cache = VPNDetection(cache=False)
```

### Private and reserved addresses

Private, loopback, link-local, documentation and multicast addresses (and their IPv6 equivalents, including the 6to4 and Teredo ranges) can never be VPN or proxy infrastructure. The library answers them locally, so they cost no request and no quota:

```python
result = client.lookup("192.168.1.1")
result.is_bogon   # True, this answer was computed rather than served
result.is_vpn     # False
```

The check is available on the client, which is handy when your inputs are addresses anyway:

```python
client.is_bogon("10.0.0.1")   # True
client.is_bogon("8.8.8.8")    # False
```

It is also importable on its own, if you want it without a client:

```python
from vpndetection import is_bogon

is_bogon("10.0.0.1")   # True
```

### Errors

Failures raise a `VPNDetectionError` carrying a `kind` and a `retryable` flag:

```python
from vpndetection import VPNDetectionError

try:
    client.lookup("1.1.1.1")
except VPNDetectionError as err:
    print(err.kind, err.retryable)
```

`kind` is one of `bad_request`, `unauthorized`, `forbidden`, `rate_limited`, `quota_exceeded`, `server_error` or `network`.

A request that runs past its `timeout` fails with `network`. The default is 30 seconds per attempt, body included, so a retried call can take longer in total, and a database download is exempt. Set it on the client, or on a single `lookup`, `my_ip`, `my_entitlement`, `lookup_batch`, `oauth` or `database` call (the last from 5.4.0, transfers aside):

```python
client = VPNDetection(timeout=30)
result = client.lookup("45.83.91.1", timeout=2)
```

`None` means no bound on the client, and the client's own on a call. Anything else that is not a number greater than 0 raises `ValueError` where it is set, before any request is made.

**Changed in 5.3.0:** a timeout of 0 or less, NaN, infinity or a string used to be accepted, and then failed every call.

Note that `rate_limited` and `quota_exceeded` both arrive as HTTP 429 and are not the same thing. A rate limit is when the API faces extreme traffic bursts and so retrying later works; but a spent quota needs your allowance raised or the window to roll over. The library retries rate limits for you, but not if your quota is exceeded.

### Database downloads

If your key carries the `db.download` scope, the licensed databases are available through `client.database`. `list` answers database families, and the ids the other calls take come from each family's `versions`. There are three ways to get a database: the time-limited link, the bytes, or straight to a file, which streams so nothing bigger than a chunk is ever held in memory:

```python
databases = client.database.list()

url = client.database.download_url("vpn_ip_extended_v1", "mmdb")
raw = client.database.download_bytes("cdn_ip_v1", "csvgz")
written = client.database.download("vpn_ip_extended_v1", "mmdb", "./vpn_ip_extended_v1.mmdb")
```

`DATABASE_FORMATS`, `STANDINGS` and `LICENSE_TYPES` hold the published formats and the values a family's `standing` and `license_type` can take, at runtime, for checking one that came from a flag or a form before you make a call.

`download_bytes` holds the whole file in memory, and the catalog runs from `cdn_ip_v1` at 10 KB to `resproxy_ip_90d_v1` at 1.79 GB, so use `download` for anything you have not measured.

From 5.4.0, `list`, `metadata`, `checksums`, `downloads` and `download_url` each take a keyword-only `timeout` in seconds, bounding each attempt at that one call in place of the client's:

```python
catalog = client.database.list(timeout=5)
sums = client.database.checksums("vpn_ip_extended_v1", "mmdb", timeout=5)
```

`download` and `download_bytes` deliberately take no `timeout` and raise `TypeError` if handed one, rather than accepting it and quietly doing nothing: a transfer runs to gigabytes and minutes, so any bound that suits a JSON call would abandon a healthy download. `download_url` does take one, because minting the link is an ordinary API request - it bounds that request, not whatever you do with the link afterwards.

### Sign in with OAuth (device flow)

A program running on someone's own machine can let them sign in with a browser and pick one of their API keys, instead of asking them to paste it:

```python
from vpndetection import VPNDetection

with VPNDetection() as signin:
    device = signin.oauth.device_authorization(
        "your-client-id", scope="account.read apikeys.read apikeys.reveal"
    )
    print(f"Open {device.verification_uri} and enter {device.user_code}")
    tokens = signin.oauth.poll_device_token("your-client-id", device)

if tokens.apikey is None:
    raise SystemExit("No API key was picked")
client = VPNDetection(tokens.apikey)
```

A refusal raises `OauthAccessDeniedError` and a code that ran out raises `OauthExpiredTokenError`, and client IDs are issued on request from support@vpndetection.io. `client.oauth.revoke("your-client-id", tokens.refresh_token)` signs the machine out.

### Fields your plan does not include

Only `ip` and `is_vpn` come back on every plan. The rest are `None` when your plan does not include them, which means "not in your plan" rather than "checked, and no".

```python
result.flagged("is_hosting")   # False rather than None on a plan without it
result.is_hosting is None      # True when hosting is not in your plan
```

## Other Libraries

There are official VPNDetection client libraries available for many languages including PHP, Python, Go, Java, Ruby, and many popular frameworks such as Django, Rails, and Laravel. See our GitHub at https://github.com/vpndetection-io for more.

## About VPNDetection

VPN Detection API: Accurate anonymity detection identifying VPNs, residential proxies, hosting servers, Tor nodes, CDNs, relays and more.

[<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" width="96"/>](https://vpndetection.io/)

## License

This project is licensed under the [MIT License](LICENSE).

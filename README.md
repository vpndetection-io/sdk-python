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

### Batch lookup

You can do batch lookups with a list, which parallelizes requests for you efficiently:

```python
results = client.lookup_batch(["45.83.91.1", "8.8.8.8", "1.1.1.1"])

for ip, result in results.items():
    if isinstance(result, Exception):
        print(f"{ip}: {result}")
        continue
    print(f"{ip}: {result.is_vpn}")
```

Results are keyed by address, so duplicates in your list collapse into a single request and one address failing never loses the rest.

Concurrency and other variables are configurable per-call:

```python
results = client.lookup_batch(many_ips, concurrency=32, retries=4)
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

Note that `rate_limited` and `quota_exceeded` both arrive as HTTP 429 and are not the same thing. A rate limit is when the API faces extreme traffic bursts and so retrying later works; but a spent quota needs your allowance raised or the window to roll over. The library retries rate limits for you, but not if your quota is exceeded.

### Database downloads

If your key carries the `db.download` scope, the licensed datasets are available through `client.database`. `list` answers dataset families, and the ids the other calls take come from each family's `versions`. There are three ways to get a database: the time-limited link, the bytes, or straight to a file, which streams so nothing bigger than a chunk is ever held in memory:

```python
datasets = client.database.list()

url = client.database.download_url("vpn_ip_extended_v1", "mmdb")
raw = client.database.download_bytes("cdn_ip_v1", "csvgz")
written = client.database.download("vpn_ip_extended_v1", "mmdb", "./vpn_ip_extended_v1.mmdb")
```

`download_bytes` holds the whole file in memory, and the catalog runs from `cdn_ip_v1` at 10 KB to `resproxy_ip_90d_v1` at 1.79 GB, so use `download` for anything you have not measured.

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

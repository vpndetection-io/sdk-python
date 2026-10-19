# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 5.4.2 are described by their release commits.

## 5.10.0 - 2026-10-19

### Features

- Re-pin the spec to 2026.10.19: num_ports and num_proxies in the pubproxy detail ([`9d74815`](https://github.com/vpndetection-io/sdk-python/commit/9d74815fcaa1f153dd9fe34016cc0ee2a7380360))

## 5.9.0 - 2026-10-18

### Features

- Re-pin the spec to 2026.10.18: is_pubproxy and the pubproxy detail ([`9935f6c`](https://github.com/vpndetection-io/sdk-python/commit/9935f6c0571754e05a50b21051ab1c977c965b15))

## 5.8.0 - 2026-10-17

### Features

- Re-pin the spec to 2026.10.16: dynamic client registration ([`ba70f10`](https://github.com/vpndetection-io/sdk-python/commit/ba70f108b023480203ed2e2afa0c6f9113c651eb))

## 5.7.3 - 2026-10-16

### Fixes

- Re-pin the spec to 2026.10.15: descriptions in US spelling ([`f8795fc`](https://github.com/vpndetection-io/sdk-python/commit/f8795fcb1353b678ab9aeeae9fe04cfdc53f5aef))

## 5.7.2 - 2026-10-15

### Fixes

- Read Retry-After as whole seconds or an HTTP date, nothing else ([`65e7850`](https://github.com/vpndetection-io/sdk-python/commit/65e785016e8196388be4ec49d9a40b2293a6f928))
- Trim the key and the base URL, and refuse a key no header can carry ([`3dd5e91`](https://github.com/vpndetection-io/sdk-python/commit/3dd5e917740454491b943e0b245c69f7a3da7717))
- Classify a 4xx by status, and fail an unreadable 2xx with its status ([`04f9f06`](https://github.com/vpndetection-io/sdk-python/commit/04f9f067361ee5e8a1ce61b9f4b8842740eb67e3))

## 5.7.1 - 2026-10-10

### Fixes

- Re-pin the spec to 2026.10.09: rotating a key needs apikeys.reveal ([`43b0e17`](https://github.com/vpndetection-io/sdk-python/commit/43b0e17da8b6de44bba8c8e8558ecc819a905fce))

## 5.7.0 - 2026-10-06

### Features

- Add the authorization code sign-in, with PKCE ([`136d47c`](https://github.com/vpndetection-io/sdk-python/commit/136d47ca847f7c9003aa51430024d03f02dbee47))

## 5.6.1 - 2026-10-04

### Fixes

- Re-pin the spec to 2026.10.03: metadata needs no license ([`ed0b251`](https://github.com/vpndetection-io/sdk-python/commit/ed0b25152f520b1b7782a39152601d7a20ea1d36))

## 5.6.0 - 2026-10-03

### Features

- Add Guard, a block condition one view applies to the attached answer ([`feba979`](https://github.com/vpndetection-io/sdk-python/commit/feba979ad967533bf8935888ca5d0c53d56bf5e3))

## 5.5.3 - 2026-10-02

### Fixes

- Bound the poll's wait, a long Retry-After and a timeout past 292 years ([`147e07b`](https://github.com/vpndetection-io/sdk-python/commit/147e07b8d55f10f35a58b46833be063a603e93dd))

## 5.5.2 - 2026-09-29

### Fixes

- Recognize 26 more reserved ranges as bogons, as the API does ([`7897696`](https://github.com/vpndetection-io/sdk-python/commit/7897696b8ccdef1df6a2c4fd196d68684f7d89ed))

## 5.5.1 - 2026-09-28

### Fixes

- Judge an IPv4-mapped address as the IPv4 address it carries ([`9f8909a`](https://github.com/vpndetection-io/sdk-python/commit/9f8909a99cc07a6711adceb99bb57842dae773fc))

## 5.5.0 - 2026-09-27

### Features

- Re-pin the spec to 2026.09.26, adding client_id_metadata_document_supported ([`618387d`](https://github.com/vpndetection-io/sdk-python/commit/618387d61fda8ee2bdbea10d6eaed04029a39f91))

## 5.4.2 - 2026-09-25

### Fixes

- Share one request per address between concurrent misses ([`4287790`](https://github.com/vpndetection-io/sdk-python/commit/42877901b0dd218126520b67d9c96eff688da459))

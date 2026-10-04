# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 5.4.2 are described by their release commits.

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

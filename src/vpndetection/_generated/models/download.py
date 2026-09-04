from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.download_outcome import DownloadOutcome

T = TypeVar("T", bound="Download")


@_attrs_define
class Download:
    """One download ATTEMPT, refusals included - a denial is what answers "it
    stopped working", so they are listed rather than dropped.

        Attributes:
            dataset_id (str):
            format_ (str):
            outcome (DownloadOutcome):
            sample (bool): The evaluation sample rather than the database itself.
            bytes_ (int | None): Object size at redirect time, NOT bytes delivered: the transfer is a
                presigned redirect straight to object storage, so we never observe it.
            http_status (int | None):
            apikey_id (None | str): The key that made the request. Null when the org acted through the
                console rather than through a key.
            client_ip (None | str):
            user_agent (None | str):
            created (datetime.datetime):
    """

    dataset_id: str
    format_: str
    outcome: DownloadOutcome
    sample: bool
    bytes_: int | None
    http_status: int | None
    apikey_id: None | str
    client_ip: None | str
    user_agent: None | str
    created: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        format_ = self.format_

        outcome = self.outcome.value

        sample = self.sample

        bytes_: int | None
        bytes_ = self.bytes_

        http_status: int | None
        http_status = self.http_status

        apikey_id: None | str
        apikey_id = self.apikey_id

        client_ip: None | str
        client_ip = self.client_ip

        user_agent: None | str
        user_agent = self.user_agent

        created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_id": dataset_id,
                "format": format_,
                "outcome": outcome,
                "sample": sample,
                "bytes": bytes_,
                "http_status": http_status,
                "apikey_id": apikey_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "created": created,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        dataset_id = d.pop("dataset_id")

        format_ = d.pop("format")

        outcome = DownloadOutcome(d.pop("outcome"))

        sample = d.pop("sample")

        def _parse_bytes_(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        bytes_ = _parse_bytes_(d.pop("bytes"))

        def _parse_http_status(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        http_status = _parse_http_status(d.pop("http_status"))

        def _parse_apikey_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        apikey_id = _parse_apikey_id(d.pop("apikey_id"))

        def _parse_client_ip(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        client_ip = _parse_client_ip(d.pop("client_ip"))

        def _parse_user_agent(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_agent = _parse_user_agent(d.pop("user_agent"))

        created = datetime.datetime.fromisoformat(d.pop("created"))

        download = cls(
            dataset_id=dataset_id,
            format_=format_,
            outcome=outcome,
            sample=sample,
            bytes_=bytes_,
            http_status=http_status,
            apikey_id=apikey_id,
            client_ip=client_ip,
            user_agent=user_agent,
            created=created,
        )

        download.additional_properties = d
        return download

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

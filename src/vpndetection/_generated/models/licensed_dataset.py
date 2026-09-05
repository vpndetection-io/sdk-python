from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.licensed_dataset_license_type import LicensedDatasetLicenseType
from ..models.licensed_dataset_standing import LicensedDatasetStanding
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.licensed_version import LicensedVersion


T = TypeVar("T", bound="LicensedDataset")


@_attrs_define
class LicensedDataset:
    """One dataset FAMILY your organization is licensed for. A license covers
    the family, while a download names a specific version, so the ids you
    pass to the download and checksum endpoints come from `versions`.

        Attributes:
            base (str): The dataset family, e.g. `vpn_ip`. What the license is held against. Example: vpn_ip.
            name (str):  Example: VPN IP.
            license_type (LicensedDatasetLicenseType): What your license permits you to do with the data.
            in_term (bool): False when the license has lapsed; downloads are refused.
            standing (LicensedDatasetStanding): `licensed` is a live grant, `expired` one whose term has ended, and
                `unlicensed` a dataset published but never bought.
            versions (list[LicensedVersion]): Every published version of this family. The `id` here is what the
                download and checksum endpoints take.
            summary (str | Unset):
            starts (datetime.datetime | None | Unset):
            expires (datetime.datetime | None | Unset): Null when the license does not expire.
    """

    base: str
    name: str
    license_type: LicensedDatasetLicenseType
    in_term: bool
    standing: LicensedDatasetStanding
    versions: list[LicensedVersion]
    summary: str | Unset = UNSET
    starts: datetime.datetime | None | Unset = UNSET
    expires: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base = self.base

        name = self.name

        license_type = self.license_type.value

        in_term = self.in_term

        standing = self.standing.value

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        summary = self.summary

        starts: None | str | Unset
        if isinstance(self.starts, Unset):
            starts = UNSET
        elif isinstance(self.starts, datetime.datetime):
            starts = self.starts.isoformat()
        else:
            starts = self.starts

        expires: None | str | Unset
        if isinstance(self.expires, Unset):
            expires = UNSET
        elif isinstance(self.expires, datetime.datetime):
            expires = self.expires.isoformat()
        else:
            expires = self.expires

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base": base,
                "name": name,
                "license_type": license_type,
                "in_term": in_term,
                "standing": standing,
                "versions": versions,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if starts is not UNSET:
            field_dict["starts"] = starts
        if expires is not UNSET:
            field_dict["expires"] = expires

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.licensed_version import LicensedVersion

        d = dict(src_dict)
        base = d.pop("base")

        name = d.pop("name")

        license_type = LicensedDatasetLicenseType(d.pop("license_type"))

        in_term = d.pop("in_term")

        standing = LicensedDatasetStanding(d.pop("standing"))

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = LicensedVersion.from_dict(versions_item_data)

            versions.append(versions_item)

        summary = d.pop("summary", UNSET)

        def _parse_starts(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                starts_type_0 = datetime.datetime.fromisoformat(data)

                return starts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        starts = _parse_starts(d.pop("starts", UNSET))

        def _parse_expires(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_type_0 = datetime.datetime.fromisoformat(data)

                return expires_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires = _parse_expires(d.pop("expires", UNSET))

        licensed_dataset = cls(
            base=base,
            name=name,
            license_type=license_type,
            in_term=in_term,
            standing=standing,
            versions=versions,
            summary=summary,
            starts=starts,
            expires=expires,
        )

        licensed_dataset.additional_properties = d
        return licensed_dataset

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

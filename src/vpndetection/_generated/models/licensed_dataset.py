from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.licensed_dataset_license_type import LicensedDatasetLicenseType
from ..models.licensed_dataset_standing import LicensedDatasetStanding

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
            summary (str):
            license_type (LicensedDatasetLicenseType): What your license permits you to do with the data.
            starts (datetime.datetime | None):
            expires (datetime.datetime | None): A hard stop. Null when the license has no end date, which is the normal case
                for a rolling agreement, and when there is no license. A rolling license reports its turnover date in renews_at
                instead.
            renews_at (datetime.datetime | None): When a rolling license next renews. Null when the license has no defined
                term, when expires sets a hard stop instead, and when there is no license.
            notice_due_at (datetime.datetime | None): The last day notice of non-renewal can be given for the term ending at
                renews_at. Null whenever renews_at is, and when the agreement records no notice period.
            in_term (bool): False when the license has lapsed; downloads are refused.
            standing (LicensedDatasetStanding): `licensed` is a live grant, `expired` one whose term has ended, and
                `unlicensed` a dataset published but never bought.
            versions (list[LicensedVersion]): Every published version of this family. The `id` here is what the
                download and checksum endpoints take.
    """

    base: str
    name: str
    summary: str
    license_type: LicensedDatasetLicenseType
    starts: datetime.datetime | None
    expires: datetime.datetime | None
    renews_at: datetime.datetime | None
    notice_due_at: datetime.datetime | None
    in_term: bool
    standing: LicensedDatasetStanding
    versions: list[LicensedVersion]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base = self.base

        name = self.name

        summary = self.summary

        license_type = self.license_type.value

        starts: None | str
        if isinstance(self.starts, datetime.datetime):
            starts = self.starts.isoformat()
        else:
            starts = self.starts

        expires: None | str
        if isinstance(self.expires, datetime.datetime):
            expires = self.expires.isoformat()
        else:
            expires = self.expires

        renews_at: None | str
        if isinstance(self.renews_at, datetime.datetime):
            renews_at = self.renews_at.isoformat()
        else:
            renews_at = self.renews_at

        notice_due_at: None | str
        if isinstance(self.notice_due_at, datetime.datetime):
            notice_due_at = self.notice_due_at.isoformat()
        else:
            notice_due_at = self.notice_due_at

        in_term = self.in_term

        standing = self.standing.value

        versions = []
        for versions_item_data in self.versions:
            versions_item = versions_item_data.to_dict()
            versions.append(versions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base": base,
                "name": name,
                "summary": summary,
                "license_type": license_type,
                "starts": starts,
                "expires": expires,
                "renews_at": renews_at,
                "notice_due_at": notice_due_at,
                "in_term": in_term,
                "standing": standing,
                "versions": versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.licensed_version import LicensedVersion

        d = dict(src_dict)
        base = d.pop("base")

        name = d.pop("name")

        summary = d.pop("summary")

        license_type = LicensedDatasetLicenseType(d.pop("license_type"))

        def _parse_starts(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                starts_type_0 = datetime.datetime.fromisoformat(data)

                return starts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        starts = _parse_starts(d.pop("starts"))

        def _parse_expires(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_type_0 = datetime.datetime.fromisoformat(data)

                return expires_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        expires = _parse_expires(d.pop("expires"))

        def _parse_renews_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                renews_at_type_0 = datetime.datetime.fromisoformat(data)

                return renews_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        renews_at = _parse_renews_at(d.pop("renews_at"))

        def _parse_notice_due_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                notice_due_at_type_0 = datetime.datetime.fromisoformat(data)

                return notice_due_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        notice_due_at = _parse_notice_due_at(d.pop("notice_due_at"))

        in_term = d.pop("in_term")

        standing = LicensedDatasetStanding(d.pop("standing"))

        versions = []
        _versions = d.pop("versions")
        for versions_item_data in _versions:
            versions_item = LicensedVersion.from_dict(versions_item_data)

            versions.append(versions_item)

        licensed_dataset = cls(
            base=base,
            name=name,
            summary=summary,
            license_type=license_type,
            starts=starts,
            expires=expires,
            renews_at=renews_at,
            notice_due_at=notice_due_at,
            in_term=in_term,
            standing=standing,
            versions=versions,
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

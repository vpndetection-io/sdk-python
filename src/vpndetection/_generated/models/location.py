from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Location")


@_attrs_define
class Location:
    """Where the address is, to the country: the fields of our IP Country
    database. Free and paid plans. Each field is present whenever the
    object is, so an address in no country, or a private one, answers
    empty strings.

        Attributes:
            continent (str): Continent code: AF, AN (Antarctica), AS, EU, NA, OC or SA. Example: EU.
            continent_name (str): Continent name. Example: Europe.
            country (str): ISO 3166-1 alpha-2 country code. Example: AT.
            country_name (str): Country name. Example: Austria.
            timezone (str): IANA timezone of the address. Example: Europe/Vienna.
            currency_code (str): ISO 4217 code of the country's currency, where there is one. Example: EUR.
            currency_name (str): Name of the country's currency, where there is one. Example: Euro.
            currency_symbol (str): Symbol of the country's currency, where known. Example: €.
            flag_emoji (str): The country's flag, as an emoji. Example: 🇦🇹.
            flag_unicode (str): The Unicode code points of the flag emoji. Example: U+1F1E6 U+1F1F9.
    """

    continent: str
    continent_name: str
    country: str
    country_name: str
    timezone: str
    currency_code: str
    currency_name: str
    currency_symbol: str
    flag_emoji: str
    flag_unicode: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        continent = self.continent

        continent_name = self.continent_name

        country = self.country

        country_name = self.country_name

        timezone = self.timezone

        currency_code = self.currency_code

        currency_name = self.currency_name

        currency_symbol = self.currency_symbol

        flag_emoji = self.flag_emoji

        flag_unicode = self.flag_unicode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "continent": continent,
                "continent_name": continent_name,
                "country": country,
                "country_name": country_name,
                "timezone": timezone,
                "currency_code": currency_code,
                "currency_name": currency_name,
                "currency_symbol": currency_symbol,
                "flag_emoji": flag_emoji,
                "flag_unicode": flag_unicode,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        continent = d.pop("continent")

        continent_name = d.pop("continent_name")

        country = d.pop("country")

        country_name = d.pop("country_name")

        timezone = d.pop("timezone")

        currency_code = d.pop("currency_code")

        currency_name = d.pop("currency_name")

        currency_symbol = d.pop("currency_symbol")

        flag_emoji = d.pop("flag_emoji")

        flag_unicode = d.pop("flag_unicode")

        location = cls(
            continent=continent,
            continent_name=continent_name,
            country=country,
            country_name=country_name,
            timezone=timezone,
            currency_code=currency_code,
            currency_name=currency_name,
            currency_symbol=currency_symbol,
            flag_emoji=flag_emoji,
            flag_unicode=flag_unicode,
        )

        location.additional_properties = d
        return location

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

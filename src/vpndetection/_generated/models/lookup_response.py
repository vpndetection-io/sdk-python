from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.abuse_contact import AbuseContact
    from ..models.asn import Asn
    from ..models.bit_torrent_detail import BitTorrentDetail
    from ..models.bot_detail import BotDetail
    from ..models.carrier_detail import CarrierDetail
    from ..models.class_detail import ClassDetail
    from ..models.company import Company
    from ..models.dns_resolver_detail import DnsResolverDetail
    from ..models.location import Location
    from ..models.proxy_detail import ProxyDetail
    from ..models.pubproxy_detail import PubproxyDetail
    from ..models.satellite_detail import SatelliteDetail
    from ..models.smtp_detail import SmtpDetail
    from ..models.ssh_detail import SshDetail
    from ..models.user_agent_verdict import UserAgentVerdict
    from ..models.vpn_detail import VpnDetail
    from ..models.web_detail import WebDetail


T = TypeVar("T", bound="LookupResponse")


@_attrs_define
class LookupResponse:
    """The union of every tier's answer. Every answer carries `ip`, `is_bogon`,
    `is_vpn`, the Tor and relay members, `is_anycast`, `hostname`, `location` and
    `asn`, with or without a key;
    each remaining field is present when your tier includes it, and absent
    otherwise. A client that must work across plans should treat an absent
    flag as unknown rather than as `false`.

        Attributes:
            ip (str): The address that was looked up, normalized. Example: 1.1.1.1.
            is_vpn (bool): Whether the address is VPN infrastructure. Keys off presence in the
                VPN dataset, so an unattributed range with no provider is still
                `true`.
            is_bogon (bool | Unset): Whether the address is reserved space (RFC 1918, loopback, link-local,
                documentation ranges and their IPv6 equivalents), answered from the
                address alone. Every answer, with or without a key.
            is_hosting (bool | Unset): Whether the address belongs to a hosting or cloud provider. Paid plans.
            is_relay (bool | Unset): Whether the address is privacy relay or enterprise web gateway egress, such as iCloud
                Private Relay or Zscaler. Every answer, with or without a key.
            is_tor (bool | Unset): Whether the address is a Tor node. Every answer, with or without a key.
            is_cdn (bool | Unset): Whether the address belongs to a CDN. Paid plans.
            is_bot (bool | Unset): Whether an automated client uses the address, such as a search engine's or an AI
                company's crawler, an uptime monitor, an internet scanner or a webhook sender. `bot` says whose, what it does
                and whether its operator vouches for the address. Every answer, with or without a key.
            is_resproxy (bool | Unset): Whether the address was seen in a residential proxy pool. Paid plans.
            is_dcproxy (bool | Unset): Whether the address is one a datacenter proxy service sells or runs on, a proxy
                company's own ranges included. Paid plans.
            is_mobproxy (bool | Unset): Whether the address was seen in a mobile proxy pool. Paid plans.
            is_pubproxy (bool | Unset): Whether a public proxy, one anyone can connect through, listens on the address or
                sends its traffic out from it. Paid plans.
            is_anycast (bool | Unset): Whether the address is announced from many places at once, as a public DNS resolver's
                or a CDN's edge is. Every answer, with or without a key.
            is_carrier (bool | Unset): Whether the address is a mobile carrier's, where many phones can share one address.
                Paid plans.
            is_satellite (bool | Unset): Whether the address is a satellite operator's. Paid plans.
            is_ssh (bool | Unset): Whether an SSH server answered on the address. Paid plans.
            is_smtp (bool | Unset): Whether a mail server answered on the address. Paid plans.
            is_web (bool | Unset): Whether a web server answered on the address, on port 80 or 443. Paid plans.
            is_dns_resolver (bool | Unset): Whether an open DNS resolver answered on the address. Paid plans.
            is_bittorrent (bool | Unset): Whether a BitTorrent client was seen on the address in the last 90 days. Paid
                plans.
            vpn (VpnDetail | Unset): What is known about the VPN attribution. Every key is present when the
                object is populated, empty values included; the object is `{}` when
                `is_vpn` is false.
            hosting (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            relay (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            tor (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            cdn (ClassDetail | Unset): The shared detail shape for the hosting, relay, tor and cdn datasets.
                Every key is present when the object is populated; the object is `{}`
                when its flag is false.
            bot (BotDetail | Unset): Bot IP's row: whose bot uses the address, the bots it serves or claimed to be, what
                they do, and how that is known.
            resproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. An address that leaves
                the window keeps its flag and the values of its last day in it, so
                `last_seen` is what says how recent they are. Every key is present when
                the object is populated; the object is `{}` when its flag is false.
            dcproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. An address that leaves
                the window keeps its flag and the values of its last day in it, so
                `last_seen` is what says how recent they are. Every key is present when
                the object is populated; the object is `{}` when its flag is false.
            mobproxy (ProxyDetail | Unset): The shared detail shape for the residential, datacenter and mobile proxy
                families, measured over a rolling 90 day window. An address that leaves
                the window keeps its flag and the values of its last day in it, so
                `last_seen` is what says how recent they are. Every key is present when
                the object is populated; the object is `{}` when its flag is false.
            pubproxy (PubproxyDetail | Unset): The address in Public Proxy IP, open proxies anyone can connect
                through, measured over a rolling 90 day window. An address that leaves
                the window keeps its flag and the values of its last day in it, so
                `last_seen` is what says how recent they are. An address is either
                end of a proxy, or both: where it listens, and where its traffic
                leaves from. Every key is present when the object is populated; the
                object is `{}` when `is_pubproxy` is false.
            carrier (CarrierDetail | Unset): The mobile network whose space the address is, from our Carrier IP
                database. Every key is present when the object is populated; the object
                is `{}` when `is_carrier` is false.
            satellite (SatelliteDetail | Unset): The satellite operator whose space the address is, from our Satellite IP
                database. Every key is present when the object is populated; the object
                is `{}` when `is_satellite` is false.
            ssh (SshDetail | Unset): The SSH server that answered on the address, from our SSH IP database.
                Every key is present when the object is populated; the object is `{}`
                when `is_ssh` is false.
            smtp (SmtpDetail | Unset): The mail server that answered on the address, from our SMTP IP database.
                Every key is present when the object is populated; the object is `{}`
                when `is_smtp` is false.
            web (list[WebDetail] | Unset): Detail for `is_web`: a row per port that answered, lowest first, and `[]` when
                false. Paid plans.
            dns_resolver (DnsResolverDetail | Unset): The open DNS resolver that answered on the address, from our DNS
                Resolver IP database. Every key is present when the object is populated;
                the object is `{}` when `is_dns_resolver` is false.
            bittorrent (BitTorrentDetail | Unset): BitTorrent clients seen on the address over the last 90 days, from our
                BitTorrent IP database. Every key is present when the object is
                populated; the object is `{}` when `is_bittorrent` is false.
            location (Location | Unset): Where the address is: the fields of our IP Country database on every
                answer, with or without a key, and our IP Geolocation database's finer
                ones on a paid plan. Each field your plan includes is present whenever
                the object is, so an address in no country, or a private one, answers
                empty strings and zeros.
            asn (Asn | Unset): The autonomous system that announces the address. Every answer, with or
                without a key.
                Each field is present whenever the object is: `asn` is 0 and the rest
                empty where no announcement covers the address.
            company (Company | Unset): Who uses the address, from our IP Company database. Paid plans. Every
                key is present whenever the object is: empty strings where no record
                covers the address.
            hostname (str | Unset): The name the address's reverse DNS (PTR) record points to, from our IP RDNS database; an
                empty string when it has none. Every answer, with or without a key.
            abuse (AbuseContact | Unset): Where to report abuse from the address, from our IP Abuse Contact
                database. Paid plans. Every key is present whenever the object is: empty
                strings where no record covers the address.
            user_agent (UserAgentVerdict | Unset):
            trial_expired (bool | Unset): On every answer to a key on the free plan, and on no other: `false`
                while its organization's trial of every field lasts, `true` once the
                answer has Unlimited's.
            cap_reached (bool | Unset): On every answer to a key on a paid plan, and on no other: `false`
                while the answer has every field, `true` once its organization's
                overage cap is reached and the answer has Unlimited's. Lookups
                answered past the cap are not billed; raising or removing the cap in
                Billing turns it `false` again.
    """

    ip: str
    is_vpn: bool
    is_bogon: bool | Unset = UNSET
    is_hosting: bool | Unset = UNSET
    is_relay: bool | Unset = UNSET
    is_tor: bool | Unset = UNSET
    is_cdn: bool | Unset = UNSET
    is_bot: bool | Unset = UNSET
    is_resproxy: bool | Unset = UNSET
    is_dcproxy: bool | Unset = UNSET
    is_mobproxy: bool | Unset = UNSET
    is_pubproxy: bool | Unset = UNSET
    is_anycast: bool | Unset = UNSET
    is_carrier: bool | Unset = UNSET
    is_satellite: bool | Unset = UNSET
    is_ssh: bool | Unset = UNSET
    is_smtp: bool | Unset = UNSET
    is_web: bool | Unset = UNSET
    is_dns_resolver: bool | Unset = UNSET
    is_bittorrent: bool | Unset = UNSET
    vpn: VpnDetail | Unset = UNSET
    hosting: ClassDetail | Unset = UNSET
    relay: ClassDetail | Unset = UNSET
    tor: ClassDetail | Unset = UNSET
    cdn: ClassDetail | Unset = UNSET
    bot: BotDetail | Unset = UNSET
    resproxy: ProxyDetail | Unset = UNSET
    dcproxy: ProxyDetail | Unset = UNSET
    mobproxy: ProxyDetail | Unset = UNSET
    pubproxy: PubproxyDetail | Unset = UNSET
    carrier: CarrierDetail | Unset = UNSET
    satellite: SatelliteDetail | Unset = UNSET
    ssh: SshDetail | Unset = UNSET
    smtp: SmtpDetail | Unset = UNSET
    web: list[WebDetail] | Unset = UNSET
    dns_resolver: DnsResolverDetail | Unset = UNSET
    bittorrent: BitTorrentDetail | Unset = UNSET
    location: Location | Unset = UNSET
    asn: Asn | Unset = UNSET
    company: Company | Unset = UNSET
    hostname: str | Unset = UNSET
    abuse: AbuseContact | Unset = UNSET
    user_agent: UserAgentVerdict | Unset = UNSET
    trial_expired: bool | Unset = UNSET
    cap_reached: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ip = self.ip

        is_vpn = self.is_vpn

        is_bogon = self.is_bogon

        is_hosting = self.is_hosting

        is_relay = self.is_relay

        is_tor = self.is_tor

        is_cdn = self.is_cdn

        is_bot = self.is_bot

        is_resproxy = self.is_resproxy

        is_dcproxy = self.is_dcproxy

        is_mobproxy = self.is_mobproxy

        is_pubproxy = self.is_pubproxy

        is_anycast = self.is_anycast

        is_carrier = self.is_carrier

        is_satellite = self.is_satellite

        is_ssh = self.is_ssh

        is_smtp = self.is_smtp

        is_web = self.is_web

        is_dns_resolver = self.is_dns_resolver

        is_bittorrent = self.is_bittorrent

        vpn: dict[str, Any] | Unset = UNSET
        if not isinstance(self.vpn, Unset):
            vpn = self.vpn.to_dict()

        hosting: dict[str, Any] | Unset = UNSET
        if not isinstance(self.hosting, Unset):
            hosting = self.hosting.to_dict()

        relay: dict[str, Any] | Unset = UNSET
        if not isinstance(self.relay, Unset):
            relay = self.relay.to_dict()

        tor: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tor, Unset):
            tor = self.tor.to_dict()

        cdn: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cdn, Unset):
            cdn = self.cdn.to_dict()

        bot: dict[str, Any] | Unset = UNSET
        if not isinstance(self.bot, Unset):
            bot = self.bot.to_dict()

        resproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.resproxy, Unset):
            resproxy = self.resproxy.to_dict()

        dcproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dcproxy, Unset):
            dcproxy = self.dcproxy.to_dict()

        mobproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.mobproxy, Unset):
            mobproxy = self.mobproxy.to_dict()

        pubproxy: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pubproxy, Unset):
            pubproxy = self.pubproxy.to_dict()

        carrier: dict[str, Any] | Unset = UNSET
        if not isinstance(self.carrier, Unset):
            carrier = self.carrier.to_dict()

        satellite: dict[str, Any] | Unset = UNSET
        if not isinstance(self.satellite, Unset):
            satellite = self.satellite.to_dict()

        ssh: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ssh, Unset):
            ssh = self.ssh.to_dict()

        smtp: dict[str, Any] | Unset = UNSET
        if not isinstance(self.smtp, Unset):
            smtp = self.smtp.to_dict()

        web: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.web, Unset):
            web = []
            for web_item_data in self.web:
                web_item = web_item_data.to_dict()
                web.append(web_item)

        dns_resolver: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dns_resolver, Unset):
            dns_resolver = self.dns_resolver.to_dict()

        bittorrent: dict[str, Any] | Unset = UNSET
        if not isinstance(self.bittorrent, Unset):
            bittorrent = self.bittorrent.to_dict()

        location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        asn: dict[str, Any] | Unset = UNSET
        if not isinstance(self.asn, Unset):
            asn = self.asn.to_dict()

        company: dict[str, Any] | Unset = UNSET
        if not isinstance(self.company, Unset):
            company = self.company.to_dict()

        hostname = self.hostname

        abuse: dict[str, Any] | Unset = UNSET
        if not isinstance(self.abuse, Unset):
            abuse = self.abuse.to_dict()

        user_agent: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user_agent, Unset):
            user_agent = self.user_agent.to_dict()

        trial_expired = self.trial_expired

        cap_reached = self.cap_reached

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ip": ip,
                "is_vpn": is_vpn,
            }
        )
        if is_bogon is not UNSET:
            field_dict["is_bogon"] = is_bogon
        if is_hosting is not UNSET:
            field_dict["is_hosting"] = is_hosting
        if is_relay is not UNSET:
            field_dict["is_relay"] = is_relay
        if is_tor is not UNSET:
            field_dict["is_tor"] = is_tor
        if is_cdn is not UNSET:
            field_dict["is_cdn"] = is_cdn
        if is_bot is not UNSET:
            field_dict["is_bot"] = is_bot
        if is_resproxy is not UNSET:
            field_dict["is_resproxy"] = is_resproxy
        if is_dcproxy is not UNSET:
            field_dict["is_dcproxy"] = is_dcproxy
        if is_mobproxy is not UNSET:
            field_dict["is_mobproxy"] = is_mobproxy
        if is_pubproxy is not UNSET:
            field_dict["is_pubproxy"] = is_pubproxy
        if is_anycast is not UNSET:
            field_dict["is_anycast"] = is_anycast
        if is_carrier is not UNSET:
            field_dict["is_carrier"] = is_carrier
        if is_satellite is not UNSET:
            field_dict["is_satellite"] = is_satellite
        if is_ssh is not UNSET:
            field_dict["is_ssh"] = is_ssh
        if is_smtp is not UNSET:
            field_dict["is_smtp"] = is_smtp
        if is_web is not UNSET:
            field_dict["is_web"] = is_web
        if is_dns_resolver is not UNSET:
            field_dict["is_dns_resolver"] = is_dns_resolver
        if is_bittorrent is not UNSET:
            field_dict["is_bittorrent"] = is_bittorrent
        if vpn is not UNSET:
            field_dict["vpn"] = vpn
        if hosting is not UNSET:
            field_dict["hosting"] = hosting
        if relay is not UNSET:
            field_dict["relay"] = relay
        if tor is not UNSET:
            field_dict["tor"] = tor
        if cdn is not UNSET:
            field_dict["cdn"] = cdn
        if bot is not UNSET:
            field_dict["bot"] = bot
        if resproxy is not UNSET:
            field_dict["resproxy"] = resproxy
        if dcproxy is not UNSET:
            field_dict["dcproxy"] = dcproxy
        if mobproxy is not UNSET:
            field_dict["mobproxy"] = mobproxy
        if pubproxy is not UNSET:
            field_dict["pubproxy"] = pubproxy
        if carrier is not UNSET:
            field_dict["carrier"] = carrier
        if satellite is not UNSET:
            field_dict["satellite"] = satellite
        if ssh is not UNSET:
            field_dict["ssh"] = ssh
        if smtp is not UNSET:
            field_dict["smtp"] = smtp
        if web is not UNSET:
            field_dict["web"] = web
        if dns_resolver is not UNSET:
            field_dict["dns_resolver"] = dns_resolver
        if bittorrent is not UNSET:
            field_dict["bittorrent"] = bittorrent
        if location is not UNSET:
            field_dict["location"] = location
        if asn is not UNSET:
            field_dict["asn"] = asn
        if company is not UNSET:
            field_dict["company"] = company
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if abuse is not UNSET:
            field_dict["abuse"] = abuse
        if user_agent is not UNSET:
            field_dict["user_agent"] = user_agent
        if trial_expired is not UNSET:
            field_dict["trial_expired"] = trial_expired
        if cap_reached is not UNSET:
            field_dict["cap_reached"] = cap_reached

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.abuse_contact import AbuseContact
        from ..models.asn import Asn
        from ..models.bit_torrent_detail import BitTorrentDetail
        from ..models.bot_detail import BotDetail
        from ..models.carrier_detail import CarrierDetail
        from ..models.class_detail import ClassDetail
        from ..models.company import Company
        from ..models.dns_resolver_detail import DnsResolverDetail
        from ..models.location import Location
        from ..models.proxy_detail import ProxyDetail
        from ..models.pubproxy_detail import PubproxyDetail
        from ..models.satellite_detail import SatelliteDetail
        from ..models.smtp_detail import SmtpDetail
        from ..models.ssh_detail import SshDetail
        from ..models.user_agent_verdict import UserAgentVerdict
        from ..models.vpn_detail import VpnDetail
        from ..models.web_detail import WebDetail

        d = dict(src_dict)
        ip = d.pop("ip")

        is_vpn = d.pop("is_vpn")

        is_bogon = d.pop("is_bogon", UNSET)

        is_hosting = d.pop("is_hosting", UNSET)

        is_relay = d.pop("is_relay", UNSET)

        is_tor = d.pop("is_tor", UNSET)

        is_cdn = d.pop("is_cdn", UNSET)

        is_bot = d.pop("is_bot", UNSET)

        is_resproxy = d.pop("is_resproxy", UNSET)

        is_dcproxy = d.pop("is_dcproxy", UNSET)

        is_mobproxy = d.pop("is_mobproxy", UNSET)

        is_pubproxy = d.pop("is_pubproxy", UNSET)

        is_anycast = d.pop("is_anycast", UNSET)

        is_carrier = d.pop("is_carrier", UNSET)

        is_satellite = d.pop("is_satellite", UNSET)

        is_ssh = d.pop("is_ssh", UNSET)

        is_smtp = d.pop("is_smtp", UNSET)

        is_web = d.pop("is_web", UNSET)

        is_dns_resolver = d.pop("is_dns_resolver", UNSET)

        is_bittorrent = d.pop("is_bittorrent", UNSET)

        _vpn = d.pop("vpn", UNSET)
        vpn: VpnDetail | Unset
        if isinstance(_vpn, Unset):
            vpn = UNSET
        else:
            vpn = VpnDetail.from_dict(_vpn)

        _hosting = d.pop("hosting", UNSET)
        hosting: ClassDetail | Unset
        if isinstance(_hosting, Unset):
            hosting = UNSET
        else:
            hosting = ClassDetail.from_dict(_hosting)

        _relay = d.pop("relay", UNSET)
        relay: ClassDetail | Unset
        if isinstance(_relay, Unset):
            relay = UNSET
        else:
            relay = ClassDetail.from_dict(_relay)

        _tor = d.pop("tor", UNSET)
        tor: ClassDetail | Unset
        if isinstance(_tor, Unset):
            tor = UNSET
        else:
            tor = ClassDetail.from_dict(_tor)

        _cdn = d.pop("cdn", UNSET)
        cdn: ClassDetail | Unset
        if isinstance(_cdn, Unset):
            cdn = UNSET
        else:
            cdn = ClassDetail.from_dict(_cdn)

        _bot = d.pop("bot", UNSET)
        bot: BotDetail | Unset
        if isinstance(_bot, Unset):
            bot = UNSET
        else:
            bot = BotDetail.from_dict(_bot)

        _resproxy = d.pop("resproxy", UNSET)
        resproxy: ProxyDetail | Unset
        if isinstance(_resproxy, Unset):
            resproxy = UNSET
        else:
            resproxy = ProxyDetail.from_dict(_resproxy)

        _dcproxy = d.pop("dcproxy", UNSET)
        dcproxy: ProxyDetail | Unset
        if isinstance(_dcproxy, Unset):
            dcproxy = UNSET
        else:
            dcproxy = ProxyDetail.from_dict(_dcproxy)

        _mobproxy = d.pop("mobproxy", UNSET)
        mobproxy: ProxyDetail | Unset
        if isinstance(_mobproxy, Unset):
            mobproxy = UNSET
        else:
            mobproxy = ProxyDetail.from_dict(_mobproxy)

        _pubproxy = d.pop("pubproxy", UNSET)
        pubproxy: PubproxyDetail | Unset
        if isinstance(_pubproxy, Unset):
            pubproxy = UNSET
        else:
            pubproxy = PubproxyDetail.from_dict(_pubproxy)

        _carrier = d.pop("carrier", UNSET)
        carrier: CarrierDetail | Unset
        if isinstance(_carrier, Unset):
            carrier = UNSET
        else:
            carrier = CarrierDetail.from_dict(_carrier)

        _satellite = d.pop("satellite", UNSET)
        satellite: SatelliteDetail | Unset
        if isinstance(_satellite, Unset):
            satellite = UNSET
        else:
            satellite = SatelliteDetail.from_dict(_satellite)

        _ssh = d.pop("ssh", UNSET)
        ssh: SshDetail | Unset
        if isinstance(_ssh, Unset):
            ssh = UNSET
        else:
            ssh = SshDetail.from_dict(_ssh)

        _smtp = d.pop("smtp", UNSET)
        smtp: SmtpDetail | Unset
        if isinstance(_smtp, Unset):
            smtp = UNSET
        else:
            smtp = SmtpDetail.from_dict(_smtp)

        _web = d.pop("web", UNSET)
        web: list[WebDetail] | Unset = UNSET
        if _web is not UNSET:
            web = []
            for web_item_data in _web:
                web_item = WebDetail.from_dict(web_item_data)

                web.append(web_item)

        _dns_resolver = d.pop("dns_resolver", UNSET)
        dns_resolver: DnsResolverDetail | Unset
        if isinstance(_dns_resolver, Unset):
            dns_resolver = UNSET
        else:
            dns_resolver = DnsResolverDetail.from_dict(_dns_resolver)

        _bittorrent = d.pop("bittorrent", UNSET)
        bittorrent: BitTorrentDetail | Unset
        if isinstance(_bittorrent, Unset):
            bittorrent = UNSET
        else:
            bittorrent = BitTorrentDetail.from_dict(_bittorrent)

        _location = d.pop("location", UNSET)
        location: Location | Unset
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = Location.from_dict(_location)

        _asn = d.pop("asn", UNSET)
        asn: Asn | Unset
        if isinstance(_asn, Unset):
            asn = UNSET
        else:
            asn = Asn.from_dict(_asn)

        _company = d.pop("company", UNSET)
        company: Company | Unset
        if isinstance(_company, Unset):
            company = UNSET
        else:
            company = Company.from_dict(_company)

        hostname = d.pop("hostname", UNSET)

        _abuse = d.pop("abuse", UNSET)
        abuse: AbuseContact | Unset
        if isinstance(_abuse, Unset):
            abuse = UNSET
        else:
            abuse = AbuseContact.from_dict(_abuse)

        _user_agent = d.pop("user_agent", UNSET)
        user_agent: UserAgentVerdict | Unset
        if isinstance(_user_agent, Unset):
            user_agent = UNSET
        else:
            user_agent = UserAgentVerdict.from_dict(_user_agent)

        trial_expired = d.pop("trial_expired", UNSET)

        cap_reached = d.pop("cap_reached", UNSET)

        lookup_response = cls(
            ip=ip,
            is_vpn=is_vpn,
            is_bogon=is_bogon,
            is_hosting=is_hosting,
            is_relay=is_relay,
            is_tor=is_tor,
            is_cdn=is_cdn,
            is_bot=is_bot,
            is_resproxy=is_resproxy,
            is_dcproxy=is_dcproxy,
            is_mobproxy=is_mobproxy,
            is_pubproxy=is_pubproxy,
            is_anycast=is_anycast,
            is_carrier=is_carrier,
            is_satellite=is_satellite,
            is_ssh=is_ssh,
            is_smtp=is_smtp,
            is_web=is_web,
            is_dns_resolver=is_dns_resolver,
            is_bittorrent=is_bittorrent,
            vpn=vpn,
            hosting=hosting,
            relay=relay,
            tor=tor,
            cdn=cdn,
            bot=bot,
            resproxy=resproxy,
            dcproxy=dcproxy,
            mobproxy=mobproxy,
            pubproxy=pubproxy,
            carrier=carrier,
            satellite=satellite,
            ssh=ssh,
            smtp=smtp,
            web=web,
            dns_resolver=dns_resolver,
            bittorrent=bittorrent,
            location=location,
            asn=asn,
            company=company,
            hostname=hostname,
            abuse=abuse,
            user_agent=user_agent,
            trial_expired=trial_expired,
            cap_reached=cap_reached,
        )

        lookup_response.additional_properties = d
        return lookup_response

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

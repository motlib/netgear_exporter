"""Functions to parse HTML data from switch"""

from dataclasses import asdict, dataclass
from typing import Any, TypeGuard, TypeVar

import lxml.html
from lxml.etree import _Element

_STATUS_MAP: dict[str, bool] = {"Up": True, "Down": False}
_SPEED_MAP: dict[str, int] = {"1000M": 1000, "100M": 100, "10M": 10, "No Speed": 0}
_EN_DIS_MAP: dict[str, bool] = {"Enable": True, "Disable": False}


@dataclass(frozen=True)
class PortStatus:
    """Status of a switch port"""

    port_no: int
    up: bool
    speed_setting: str
    speed_mbit_per_s: int
    flow_control: bool
    max_mtu: int


@dataclass(frozen=True)
class PortStatistics:
    """Statistics of a switch port"""

    port_no: int
    rx_bytes: int
    tx_bytes: int
    crc_error_pkts: int


@dataclass(frozen=True)
class SwitchInfo:  # pylint: disable=too-many-instance-attributes
    """Switch information"""

    product_name: str
    switch_name: str
    serial_no: str
    mac: str
    firmware_version: str
    dhcp: bool
    ip_address: str
    subnet_mask: str
    gateway_address: str

    def as_dict(self):
        """Return data as dictionary"""
        return asdict(self)


class HtmlParseException(Exception):
    """Exception class for html parser errors"""


_ItemT = TypeVar("_ItemT")


def _is_list(lst: Any, item_type: type[_ItemT]) -> TypeGuard[list[_ItemT]]:
    """Ensure that an xpath expression returns a list of _Element objects"""

    if not isinstance(lst, list):
        return False

    for item in lst:
        if not isinstance(item, item_type):
            return False

    return True


def parse_port_status(html: str) -> list[PortStatus]:
    """Parse the port status html data"""

    doc = lxml.html.document_fromstring(html)

    tr_tags = doc.xpath("//tr[@class='portID']")
    if not _is_list(tr_tags, item_type=_Element):
        raise HtmlParseException("xpath error")

    data = []

    for tr_tag in tr_tags:

        info = tr_tag.xpath("td/text()")

        if not _is_list(info, item_type=str):
            raise HtmlParseException("xpath error")

        data.append(
            PortStatus(
                port_no=int(info[0]),
                up=_STATUS_MAP[info[1].strip()],
                speed_setting=info[2].strip(),
                speed_mbit_per_s=_SPEED_MAP[info[3].strip()],
                flow_control=_EN_DIS_MAP[info[4].strip()],
                max_mtu=int(info[5]),
            )
        )

    return data


def parse_port_statistics(html: str) -> list[PortStatistics]:
    """Parse port statistics html data"""

    doc = lxml.html.document_fromstring(html)

    tr_tags = doc.xpath("//tr[@class='portID']")

    if not _is_list(tr_tags, item_type=_Element):
        raise HtmlParseException("xpath error")

    port_stats: list[PortStatistics] = []

    for port_no, tr_tag in enumerate(tr_tags, start=1):
        hidden_vals = tr_tag.xpath("input[@type='hidden']/@value")

        if not _is_list(hidden_vals, item_type=str):
            raise HtmlParseException("xpath error")

        port_stats.append(
            PortStatistics(
                port_no=port_no,
                rx_bytes=int(hidden_vals[0], base=16),
                tx_bytes=int(hidden_vals[1], base=16),
                crc_error_pkts=int(hidden_vals[2], base=16),
            )
        )

    return port_stats


def _xpath_get_text(el: _Element, xpath: str) -> str:
    lst = el.xpath(xpath)

    if not _is_list(lst, item_type=str):
        raise HtmlParseException("xpath error")

    return lst[0] if len(lst) else ""


def parse_switch_info(html: str) -> SwitchInfo:
    """Parse switch info html data"""

    doc = lxml.html.document_fromstring(html)

    trs = doc.xpath("//table[@id='tbl1']/tr")
    if not _is_list(trs, item_type=_Element):
        raise HtmlParseException("xpath error")

    prod_name = _xpath_get_text(trs[0], "td[2]/text()")
    switch_name = _xpath_get_text(trs[1], "td[2]/input/@value")
    serial = _xpath_get_text(trs[2], "td[2]/text()")
    mac = _xpath_get_text(trs[3], "td[2]/text()")
    fw = _xpath_get_text(trs[5], "td[2]/text()")
    dhcp = _xpath_get_text(trs[6], "td[2]/input[1]/@value")
    ip = _xpath_get_text(trs[7], "td[2]/input[1]/@value")
    subnet = _xpath_get_text(trs[8], "td[2]/input[1]/@value")
    gw = _xpath_get_text(trs[9], "td[2]/input[1]/@value")

    return SwitchInfo(
        product_name=prod_name,
        switch_name=switch_name,
        serial_no=serial,
        mac=mac,
        firmware_version=fw,
        dhcp=(dhcp == "1"),
        ip_address=ip,
        subnet_mask=subnet,
        gateway_address=gw,
    )


def get_rand(html: str) -> str:
    """Retrieve the seed value from the login page."""

    doc = lxml.html.document_fromstring(html)

    rand = doc.xpath("//input[@type='hidden' and @id='rand']/@value")
    if not _is_list(rand, item_type=str):
        raise HtmlParseException("Cannot extract 'rand' value from html")

    return rand[0]

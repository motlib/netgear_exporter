"""Unit tests for html parsing"""

from pathlib import Path

from ..parse_html import (
    get_rand,
    parse_port_statistics,
    parse_port_status,
    parse_switch_info,
)


def _get_content(name: str) -> str:
    """Retrieve contents of a test file"""

    this_dir = Path(__file__).parent

    with open(this_dir / "GS108Ev3" / name, "r", encoding="utf-8") as fhdl:
        html = fhdl.read()

    return html


def test_parse_switch_info() -> None:
    """Test parsing the switch info data"""

    swinfo = parse_switch_info(_get_content("switch_info.htm"))

    assert swinfo.product_name == "GS108Ev3"
    assert swinfo.switch_name == "sw1"
    assert swinfo.serial_no == "3V76755900197"
    assert swinfo.mac == "A0:40:A0:7D:A5:B9"
    assert swinfo.firmware_version == "V2.06.16EN"
    assert swinfo.dhcp is True
    assert swinfo.gateway_address == "192.168.0.254"
    assert swinfo.ip_address == "192.168.0.239"


def test_parse_port_status() -> None:
    """Test parsing the port status data"""

    status = parse_port_status(_get_content("status.htm"))

    assert len(status) == 8

    assert status[0].port_no == 1
    assert status[0].up is True
    assert status[0].speed_setting == "Auto"
    assert status[0].speed_mbit_per_s == 1000
    assert status[0].flow_control is False
    assert status[0].max_mtu == 9702


def test_parse_port_statistics() -> None:
    """Test parsing the switch info data"""

    stats = parse_port_statistics(_get_content("portStats.htm"))

    assert len(stats) == 8

    assert stats[3].port_no == 4
    assert stats[3].rx_bytes == 80407886
    assert stats[3].tx_bytes == 5434952846
    assert stats[3].crc_error_pkts == 0


def test_get_rand() -> None:
    """Test function to extract login seed value"""

    rand = get_rand(_get_content("login.htm"))

    assert rand == "1450459452"

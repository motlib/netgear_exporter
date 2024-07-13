"""Connectivity to Netgear switch"""

import hashlib
import logging
from dataclasses import dataclass

import requests

from .parse_html import (
    PortStatistics,
    PortStatus,
    get_rand,
    parse_port_statistics,
    parse_port_status,
    parse_switch_info,
)

logger = logging.getLogger(__name__)

# Timeout for http requests to the switch. As we should be in a local network,
# the timeout can be quite short.
_REQUESTS_TIMEOUT = 5


@dataclass(frozen=True)
class PortInfo:
    """Port info container combining port status and statistics"""

    port_no: int
    status: PortStatus
    statistics: PortStatistics


def _calc_md5(data: str) -> str:
    """Calculates the MD5 checksum of a string."""

    data_bytes = data.encode("utf-8")

    md5_hash = hashlib.md5()
    md5_hash.update(data_bytes)

    return md5_hash.hexdigest()


def _merge_pwd_and_seed(password: str, seed: str) -> str:
    """Merge password and seed"""

    result = ""
    index1 = 0
    index2 = 0

    while index1 < len(password) or (index2 < len(seed)):
        if index1 < len(password):
            result += password[index1]
            index1 += 1

        if index2 < len(seed):
            result += seed[index2]
            index2 += 1

    return result


def _encrypt_password(password: str, seed: str) -> str:
    """Encrypt the password with Netgear algo"""

    merged_pw = _merge_pwd_and_seed(password, seed)

    return _calc_md5(merged_pw)


def _needs_login(html: str) -> bool:
    """Return true if login is needed"""

    return '<body onload="RedirectToLoginPage();">' in html


class NetgearConnectorException(Exception):
    """Base class for all exceptions raised by NetgearConnector"""


class NetgearConnector:
    """Netgear connector retrieving status and statistics from a Netgear
    switch"""

    def __init__(self, address: str, password: str) -> None:
        self._address = address
        self._password = password
        self._session = requests.Session()

    @property
    def address(self) -> str:
        """Return the connector address"""

        return self._address

    def _retrieve_seed(self) -> str:
        """Retrieve the login seed from the router"""

        response = requests.get(
            f"http://{self._address}/login.htm", timeout=_REQUESTS_TIMEOUT
        )

        rand = get_rand(response.text)

        if not rand:
            raise NetgearConnectorException("No 'rand' value found on login page")

        return rand

    def _retrieve_html(self, url: str) -> str:
        """Try to retrieve a HTML page from the switch. Log in if necessary."""

        response = self._session.get(url, timeout=_REQUESTS_TIMEOUT)

        if _needs_login(response.text):
            logger.info(
                "Switch indicates login is required. Performing login and try again."
            )
            self.login()
        else:
            return response.text

        response = self._session.get(url, timeout=_REQUESTS_TIMEOUT)

        if _needs_login(response.text):
            raise NetgearConnectorException(f"Failed to log in for '${url}'.")

        return response.text

    def login(self):
        """Log in to the router. This retrieves the session cookie."""

        rand = self._retrieve_seed()

        data = {"password": _encrypt_password(self._password, rand)}

        self._session.post(f"http://{self._address}/login.cgi", data=data)

        if "GS108SID" not in self._session.cookies:
            raise NetgearConnectorException("Login cookie not set. Login failed.")

    def logout(self) -> None:
        """Log out from switch"""

        self._session.get(
            f"http://{self._address}/logout.cgi", timeout=_REQUESTS_TIMEOUT
        )

        self._session.cookies.clear()

    def get_port_status(self) -> list[PortStatus]:
        """Retrieve the port status of all switch ports"""

        content = self._retrieve_html(f"http://{self._address}/status.htm")

        return parse_port_status(content)

    def get_port_statistics(self) -> list[PortStatistics]:
        """Retrieve the port statistics of all switch ports"""

        content = self._retrieve_html(f"http://{self._address}/portStats.htm")

        return parse_port_statistics(html=content)

    def get_switch_info(self):
        """Retrieve the switch information"""

        content = self._retrieve_html(f"http://{self._address}/switch_info.htm")

        return parse_switch_info(html=content)

    def get_port_info(self) -> list[PortInfo]:
        """Retrieve the port info of all switch ports"""

        status = self.get_port_status()
        statistics = self.get_port_statistics()

        return [
            PortInfo(status.port_no, status, stats)
            for port_no, (status, stats) in enumerate(zip(status, statistics))
        ]

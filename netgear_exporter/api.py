"""API implementation"""

import logging

from cachetools import TTLCache, cached
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from promexp import PrometheusExporter

from . import metadata
from .connector import NetgearConnector
from .exporter import prom_exp
from .settings import settings

logger = logging.getLogger(__name__)


@cached(cache=TTLCache(maxsize=settings.cache_size, ttl=settings.cache_ttl))
def _get_connector(address: str, password: str) -> NetgearConnector:
    """Helper function to return a new netgear connector for the given address.

    This function has a cache decorator with a configured TTL, so that for the
    same address the same connector is returned and an already existing HTTP
    login session is reused. Otherwise the switch kicks you out if you attempt
    too many login attempts (even if successful) in a limited time.
    """

    return NetgearConnector(address, password)


api = FastAPI()


def _update_metrics_from_connector(
    pexp: PrometheusExporter, connector: NetgearConnector
) -> None:
    """Update the given prometheus exporter with new metric values.

    Note: We do not set the 'address' label manually to the switch IP address,
    as this is automatically done as 'instance' by Prometheus when using the
    multi-target pattern."""

    try:
        si = connector.get_switch_info()
        pis = connector.get_port_info()

        labels: dict[str, str] = {}
        labels["dhcp"] = str(int(si.dhcp))
        labels["gateway"] = si.gateway_address
        labels["netmask"] = si.subnet_mask
        labels["name"] = si.switch_name
        labels["ip"] = si.ip_address
        labels["firmware"] = si.firmware_version
        labels["mac"] = si.mac
        labels["product"] = si.product_name
        labels["sn"] = si.serial_no

        pexp.set("netgear_info", labels=labels, value=1)

        pexp.set("netgear_up", labels={}, value=1)
    except Exception as ex:  # pylint:disable=broad-exception-caught
        pexp.set("netgear_up", labels={"address": connector.address}, value=0)
        logger.error(
            f"Cannot retrieve switch information from {connector.address}: {ex}"
        )

        pexp.clear("netgear_rx_bytes_total")
        pexp.clear("netgear_tx_bytes_total")
        pexp.clear("netgear_crc_err_total")
        pexp.clear("netgear_port_up")
        pexp.clear("netgear_speed")
        pexp.clear("netgear_flow_control")

        return

    for pi in pis:
        name_vals: dict[str, float] = {
            "netgear_rx_bytes_total": pi.statistics.rx_bytes,
            "netgear_tx_bytes_total": pi.statistics.tx_bytes,
            "netgear_crc_err_total": pi.statistics.crc_error_pkts,
            "netgear_port_up": int(pi.status.up),
            "netgear_speed": pi.status.speed_mbit_per_s,
            "netgear_flow_control": int(pi.status.flow_control),
        }

        pexp.set_all(
            name_vals=name_vals,
            labels={"port": str(pi.port_no)},
        )

    return


@api.get("/probe")
async def get_probe(
    target=Query(description="Switch IP address"),
    auth_module=Query(description="Name of the auth module"),
) -> PlainTextResponse:
    """Retrieve switch metrics.

    See https://prometheus.io/docs/guides/multi-target-exporter/ for more
    information."""

    if (
        auth_module
        not in settings.auth_modules  # pylint: disable=unsupported-membership-test
    ):
        raise HTTPException(
            status_code=404, detail=f"Auth module '{auth_module}' not known."
        )

    password = settings.auth_modules[  # pylint: disable=unsubscriptable-object
        auth_module
    ]

    collector = _get_connector(target, password)

    exp = prom_exp.clone()

    _update_metrics_from_connector(exp, connector=collector)

    return PlainTextResponse(exp.render())


class InfoModel(BaseModel):
    """Data container used for returning API metadata."""

    name: str
    version: str
    docs_url: str
    metrics_url: str


@api.get("/")
async def get_root(request: Request) -> InfoModel:
    """Get API metadata"""

    info = InfoModel(
        name="netgear_exporter",
        version=metadata.VERSION,
        docs_url=f"{request.url}docs",
        metrics_url=f"{request.url}probe",
    )

    return info

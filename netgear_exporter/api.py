"""API implementation"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from promexp import MetricTypeEnum, PrometheusExporter

from . import metadata
from .connector import NetgearConnector
from .settings import settings

logger = logging.getLogger(__name__)

pexp = PrometheusExporter(hide_empty_metrics=True)

connectors: list[NetgearConnector] = []


def init():
    """Initialize the objects required by the API"""

    pexp.register(
        "netgear_build", datatype=MetricTypeEnum.GAUGE, helpstr="Build information"
    )
    pexp.set("netgear_build", labels={"version": metadata.VERSION}, value=1)

    pexp.register(
        "netgear_up", datatype=MetricTypeEnum.GAUGE, helpstr="Switch is reachable"
    )

    pexp.register("netgear_info", datatype=MetricTypeEnum.GAUGE, helpstr="Switch info")

    pexp.register(
        "netgear_rx_bytes_total",
        datatype=MetricTypeEnum.COUNTER,
        helpstr="Number of bytes received on port",
    )
    pexp.register(
        "netgear_tx_bytes_total",
        datatype=MetricTypeEnum.COUNTER,
        helpstr="Number of bytes transmitted on port",
    )
    pexp.register(
        "netgear_crc_err_total",
        datatype=MetricTypeEnum.COUNTER,
        helpstr="Number of CRC errors",
    )
    pexp.register(
        "netgear_port_up", MetricTypeEnum.GAUGE, helpstr="Switch port is connected"
    )

    pexp.register(
        "netgear_speed", MetricTypeEnum.GAUGE, helpstr="Connection speed in MBit"
    )

    pexp.register(
        "netgear_flow_control",
        MetricTypeEnum.GAUGE,
        helpstr="Port flow control enabled or disabled",
    )

    for swcfg in settings.switches:  # pylint: disable=not-an-iterable
        connectors.append(NetgearConnector(swcfg.address, swcfg.password))


api = FastAPI(on_startup=[init])


@api.get("/metrics")
def get_metrics() -> PlainTextResponse:
    """Get Prometheus metrics output"""

    for connector in connectors:
        try:
            si = connector.get_switch_info()
            pis = connector.get_port_info()

            labels: dict[str, str] = {}
            labels["address"] = connector.address
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

            pexp.set("netgear_up", labels={"address": connector.address}, value=1)
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

            continue

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
                labels={"address": connector.address, "port": str(pi.port_no)},
            )

    return PlainTextResponse(content=pexp.render())


class InfoModel(BaseModel):
    """Data container used for returning API metadata."""

    name: str
    version: str
    docs_url: str
    metrics_url: str


@api.get("/")
def get_root(request: Request) -> InfoModel:
    """Get API metadata"""

    info = InfoModel(
        name="netgear_exporter",
        version=metadata.VERSION,
        docs_url=f"{request.url}docs",
        metrics_url=f"{request.url}metrics",
    )

    return info

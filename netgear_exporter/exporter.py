"""Instantiation of the prometheus exporter"""

from netgear_exporter import metadata
from promexp import MetricTypeEnum, PrometheusExporter


def _init_exporter() -> PrometheusExporter:
    """Initialize the objects required by the API"""

    pexp = PrometheusExporter(hide_empty_metrics=True)

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

    return pexp


prom_exp = _init_exporter()

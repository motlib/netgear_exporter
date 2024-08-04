"""Exporter settings"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SwitchConfig(BaseModel):
    """Settings for a single switch"""

    address: str = Field(
        default="192.168.0.239", description="Address of the switch to monitor"
    )

    password: str = Field(default="", description="Password to connect to the switch")


class NetgearExporterSettings(BaseSettings):
    """Settings for netgear exporter"""

    interface: str = Field(
        default="0.0.0.0", description="Network interface to listen on"
    )

    port: int = Field(default=8177, description="TCP port to listen on")

    debug: bool = Field(
        default=False,
        description="Set to true for online reloading of source code changes",
    )

    switches: list[SwitchConfig] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_prefix="netgear_exporter_", cli_parse_args=True
    )


settings = NetgearExporterSettings()

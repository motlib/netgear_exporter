"""Exporter settings"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    cache_size: int = Field(
        default=32,
        description="Size of the cache of netgear connectors remembered for the /probe API.",
    )

    cache_ttl: int = Field(
        default=15 * 60,
        description="Time to life of the cached connectors for the /probe API.",
    )

    auth_modules: dict[str, str] = Field(default_factory=dict)

    model_config = SettingsConfigDict(
        env_prefix="netgear_exporter_", cli_parse_args=True
    )


settings = NetgearExporterSettings()

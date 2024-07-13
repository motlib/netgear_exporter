"""Application main entry point"""

import logging

import uvicorn

from .settings import settings

logger = logging.getLogger(__name__)


def main() -> None:
    """Application main entry point"""

    logger.info(f"Applied settings: {settings}")

    uvicorn.run(
        "netgear_exporter.api:api",
        host=settings.interface,
        port=settings.port,
        reload=settings.debug,
    )

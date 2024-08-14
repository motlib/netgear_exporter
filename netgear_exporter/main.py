"""Application main entry point"""

import logging
import sys
from signal import SIGINT, SIGTERM, signal

import uvicorn

from .settings import settings

logger = logging.getLogger(__name__)


def _exit_gracefully(signum: int, frame) -> None:
    """This function is executed as response to a SIGTERM signal. As we do not
    need to do any cleanup, it just calls exit(0) to indicate a clean shutdown.
    """

    logger.info(f"Shutting down due to signal {signum}")

    del signum
    del frame

    sys.exit(0)


def _register_sigterm() -> None:
    """Register the SIGTERM signal handler"""

    logger.info("Registering SIGTERM handler")

    signal(SIGTERM, _exit_gracefully)
    signal(SIGINT, _exit_gracefully)


def main() -> None:
    """Application main entry point"""

    logging.basicConfig(level=logging.INFO)

    logger.info(f"Applied settings: {settings}")

    _register_sigterm()

    uvicorn.run(
        "netgear_exporter.api:api",
        host=settings.interface,
        port=settings.port,
        reload=settings.debug,
    )

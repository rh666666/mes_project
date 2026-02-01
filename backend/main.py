"""Uvicorn ASGI server entry point with performance optimizations.

This module provides an optimized uvicorn server startup for the Django ASGI application.
It includes performance tuning options such as multi-worker support, uvloop event loop,
and configurable connection limits.

Examples:
    Basic usage:
        $ python main.py

    With custom workers:
        $ python main.py --workers 4

    Development mode with auto-reload:
        $ python main.py --reload

Attributes:
    DEFAULT_HOST: Default server bind address.
    DEFAULT_PORT: Default server port.
    DEFAULT_WORKERS: Default number of worker processes.
    DEFAULT_LOG_LEVEL: Default logging level.
"""

import argparse
import logging
import multiprocessing
import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

DEFAULT_HOST = os.getenv("HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("PORT", "8000"))
DEFAULT_WORKERS = int(os.getenv("WORKERS", str(multiprocessing.cpu_count())))
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
DEFAULT_RELOAD = os.getenv("RELOAD", "false").lower() == "true"
DEFAULT_ACCESS_LOG = os.getenv("ACCESS_LOG", "true").lower() == "true"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")

logger = logging.getLogger(__name__)


def get_optimal_workers() -> int:
    """Calculate optimal number of worker processes based on CPU cores.

    Returns:
        int: Recommended number of worker processes (2 * CPU cores + 1).
    """
    return multiprocessing.cpu_count() * 2 + 1


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for uvicorn server configuration.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Start the Django ASGI server with uvicorn",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help="Bind socket to this host",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Bind socket to this port",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Number of worker processes (0 = auto-detect)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=DEFAULT_RELOAD,
        help="Enable auto-reload on code changes (development mode)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Logging level",
    )
    parser.add_argument(
        "--access-log",
        action="store_true",
        default=DEFAULT_ACCESS_LOG,
        help="Enable access logging",
    )
    parser.add_argument(
        "--no-access-log",
        action="store_true",
        help="Disable access logging",
    )

    return parser.parse_args()


def run_server(args: argparse.Namespace) -> None:
    """Configure and run the uvicorn server with performance optimizations.

    Args:
        args: Parsed command line arguments containing server configuration.

    Raises:
        SystemExit: If server fails to start.
    """
    workers = args.workers if args.workers > 0 else get_optimal_workers()

    if args.reload and workers > 1:
        logger.warning("Reload mode is enabled, forcing workers to %s", 1)
        workers = 1

    access_log = args.access_log if not args.no_access_log else False

    config = uvicorn.Config(
        app="application.asgi:application",
        host=args.host,
        port=args.port,
        workers=workers if not args.reload else 1,
        reload=args.reload,
        log_level=args.log_level,
        access_log=access_log,
        loop="uvloop" if sys.platform != "win32" else "asyncio",
        http="httptools",
        lifespan="off",
        proxy_headers=True,
        forwarded_allow_ips="*",
        limit_concurrency=1000,
        backlog=2048,
        timeout_keep_alive=5,
        timeout_graceful_shutdown=30,
    )

    server = uvicorn.Server(config)

    logger.info("Starting uvicorn server on %s:%s", args.host, args.port)
    logger.info("Workers: %s", workers)
    logger.info("Reload: %s", args.reload)
    logger.info("Log level: %s", args.log_level)
    logger.info("Loop: %s", config.loop)
    logger.info("HTTP parser: %s", config.http)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error("Server error: %s", e)
        sys.exit(1)


def main() -> None:
    """Main entry point for the uvicorn server.

    Parses command line arguments and starts the server.
    """
    args = parse_arguments()
    run_server(args)


if __name__ == "__main__":
    main()

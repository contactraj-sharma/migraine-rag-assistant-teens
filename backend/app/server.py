"""Development server helper for the FastAPI app.

This module provides a small wrapper around :mod:`uvicorn` that mirrors the
recommended ``uvicorn backend.app.main:app --reload`` command while adding a
few quality-of-life improvements:

* If the default port (``8000``) is already in use, automatically search for
  the next available port and start the server there. This prevents the
  ``[Errno 48] Address already in use`` crash that is common on macOS.
* Respect ``PORT`` and ``HOST`` environment variables when explicitly set.
* Allow toggling the reload behaviour via ``UVICORN_RELOAD``.

Running ``python -m backend.app.server`` will launch the FastAPI application
with these safeguards in place.
"""

from __future__ import annotations

import errno
import os
import socket
from contextlib import closing
from typing import Optional

import uvicorn


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def _is_truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.lower() in {"1", "true", "yes", "on"}


def _find_available_port(host: str, preferred_port: int) -> int:
    """Return an available TCP port, starting from ``preferred_port``.

    The function attempts to bind to ``preferred_port`` first. If the port is
    occupied, it increments the value until a free port is found. The
    temporary binding is immediately released before returning, ensuring the
    port can be claimed by the uvicorn server afterwards.
    """

    port = preferred_port
    while True:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            # ``SO_REUSEADDR`` helps avoid TIME_WAIT collisions on restart.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError as exc:  # pragma: no cover - platform specific
                if exc.errno != errno.EADDRINUSE:
                    raise
                port += 1
                continue
            return port


def run() -> None:
    """Start the FastAPI application with smart port selection."""

    host = os.getenv("HOST", DEFAULT_HOST)

    port_env = os.getenv("PORT")
    if port_env is not None:
        try:
            preferred_port = int(port_env)
        except ValueError as exc:
            raise ValueError("PORT environment variable must be an integer") from exc
        auto_select_port = False
    else:
        preferred_port = DEFAULT_PORT
        # Allow opting out of auto-selection by setting AUTO_PORT_SELECTION=0
        auto_select_port = not os.getenv("AUTO_PORT_SELECTION") or _is_truthy(
            os.getenv("AUTO_PORT_SELECTION", "1")
        )

    reload_enabled = True
    reload_env = os.getenv("UVICORN_RELOAD")
    if reload_env is not None:
        reload_enabled = _is_truthy(reload_env)

    selected_port = preferred_port
    if auto_select_port:
        selected_port = _find_available_port(host, preferred_port)
        if selected_port != preferred_port:
            print(
                f"[devserver] Port {preferred_port} already in use, "
                f"starting on {selected_port} instead."
            )

    config = uvicorn.Config(
        "backend.app.main:app",
        host=host,
        port=selected_port,
        reload=reload_enabled,
        reload_dirs=[os.getcwd()],
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":  # pragma: no cover - convenience entrypoint
    run()

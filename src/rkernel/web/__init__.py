"""Local web UI for the recognition kernel.

Stdlib only, in keeping with the core package's zero-dependency stance.
Serves a single-page frontend plus a small JSON API over `rkernel.generate`.

    python -m rkernel.cli serve --port 8080
"""

from __future__ import annotations

from .server import serve

__all__ = ["serve"]

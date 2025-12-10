"""WSGI entrypoint for LifeOS."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path when running this file directly
ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))
# Avoid shadowing stdlib modules (e.g., stdlib `platform`) when running this
# file directly by ensuring the package directory itself is not ahead of stdlib.
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))

from lifeos import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    import os

    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5001"))
    app.run(host=host, port=port)  # nosec B104

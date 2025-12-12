"""CLI entrypoint to run the outbox dispatcher worker."""

from __future__ import annotations

import logging
import os

from lifeos import create_app
from lifeos.lifeos_platform.worker.config import DispatchConfig
from lifeos.lifeos_platform.worker.dispatcher import run_dispatcher


def main() -> None:
    logging.basicConfig(level=os.environ.get("WORKER_LOGLEVEL", "INFO"))
    env = os.environ.get("APP_ENV", "development")
    app = create_app(env)
    with app.app_context():
        run_dispatcher(DispatchConfig.from_env())


if __name__ == "__main__":
    main()

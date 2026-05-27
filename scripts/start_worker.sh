#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=".venv-spagcn/bin/python"
if [ ! -f "$VENV" ]; then
  echo "ERROR: $VENV not found. Create it with: uv venv .venv-spagcn --python 3.11" >&2
  exit 1
fi
echo "Starting ST Platform worker (polling every 5s) ..."
PYTHONPATH=src $VENV -c "
import time
import logging
from st_platform.storage.database import SessionLocal, init_db
from st_platform.workflows.service import create_platform_service
from st_platform.worker.runner import poll_runs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('worker')

init_db()
svc = create_platform_service()

logger.info('Worker started. Polling for queued runs every 5 seconds...')
while True:
    db = SessionLocal()
    try:
        count = poll_runs(
            db=db,
            runner=svc.runner,
            registry=svc.algorithm_registry,
            build_demo_bundle=svc.build_demo_dataset,
        )
        if count > 0:
            logger.info('Processed %d run(s)', count)
    except Exception:
        logger.exception('Error during poll')
    finally:
        db.close()
    time.sleep(5)
"

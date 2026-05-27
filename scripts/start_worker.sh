#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Starting ST Platform worker (polling every 5s) ..."
PYTHONPATH=src python3 -c "
import time
import logging
from st_platform.storage.database import SessionLocal, init_db
from st_platform.core.registry import AlgorithmRegistry
from st_platform.core.runner import LocalRunner
from st_platform.algorithms import build_builtin_algorithms
from st_platform.worker.runner import poll_runs
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('worker')

init_db()
registry = AlgorithmRegistry(build_builtin_algorithms())
runner = LocalRunner(registry, Path('runs'))

logger.info('Worker started. Polling for queued runs every 5 seconds...')
while True:
    db = SessionLocal()
    try:
        count = poll_runs(db=db, runner=runner, registry=registry)
        if count > 0:
            logger.info('Processed %d run(s)', count)
    except Exception:
        logger.exception('Error during poll')
    finally:
        db.close()
    time.sleep(5)
"

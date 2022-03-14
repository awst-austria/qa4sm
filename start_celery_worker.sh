#!/bin/bash
celery -A valentina worker -Ofair --max-tasks-per-child=1 --concurrency=4 -l INFO --time-limit=16000 --prefetch-multiplier=1 --statedb=run_celery/%n.state

#!/bin/bash
celery -A valentina worker --max-tasks-per-child=1 -l INFO --time-limit=16000 --prefetch-multiplier 1

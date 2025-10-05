#!/usr/bin/env bash
set -e

case "$1" in
  api)
    exec uvicorn app.main:app \
      --host 0.0.0.0 --port 8000 --workers 2
    ;;
  worker)
    exec celery -A app.mycelery.app:celery_app worker \
      --loglevel=info --concurrency=2
    ;;
  beat)
    exec celery -A app.mycelery.app:celery_app beat \
      --loglevel=info
    ;;
  flower)
    exec celery -A app.mycelery.app:celery_app flower \
      --port=5555 --loglevel=info
    ;;
  *)
    echo "Usage: $0 {api|worker|beat|flower}"
    exit 1
    ;;
esac

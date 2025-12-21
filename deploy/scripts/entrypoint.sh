#!/bin/sh
set -e

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "Running database migrations..."
  python -m flask --app lifeos.wsgi:app db upgrade head
fi

exec "$@"

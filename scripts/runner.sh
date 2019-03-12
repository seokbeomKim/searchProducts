#!/bin/bash
set -e

if [ "$1" = 'sse' ]; then
    exec flask run --no-debugger --no-reload --host=0.0.0.0
fi

exec "$@"

#!/bin/sh
set -e

if [ "$1" = 'agenda' ]; then
    python -u /agenda/agenda.py
    exit
fi

exec "$@"
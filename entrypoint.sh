#!/bin/bash

IP_HOST_MACHINE=$(/sbin/ip route|awk '/default/ { print $3 }')

if [[ "$MYSQL_HOST" == "outside.container" ]]; then
    export MYSQL_HOST="$IP_HOST_MACHINE"
fi

.venv/bin/gunicorn --workers=4 --bind 0.0.0.0:"$PORT" app:app

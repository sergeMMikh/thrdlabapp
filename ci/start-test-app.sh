#!/bin/sh
# Disposable CI-only service. Never starts or deploys a production instance.
set -eu
unset CI
ready=false
for attempt in $(seq 1 60); do
    if python -c "import os, socket; socket.create_connection((os.environ['PGHOST'], int(os.environ['PGPORT'])), 2).close()" 2>/dev/null; then
        ready=true
        break
    fi
    sleep 1
done
test "$ready" = true
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 60

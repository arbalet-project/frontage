#!/bin/bash
set -e

case "$1" in
    prod)
        echo "---> Starting in PRODUCTION mode"
        cd /usr/src/app/
        sleep 8
        exec /usr/local/bin/gunicorn server:app -w 5 -b :8123
        ;;
    dev)
        echo "---> Starting in DEV mode"
        cd /usr/src/app/
        export FLASK_DEBUG=1
        sleep 8
        exec /usr/local/bin/python server.py port 8123
        ;;
    worker)
        cd /usr/src/app/
        sleep 8
        # celery -A tasks beat &
        exec celery -A tasks worker -B --loglevel=DEBUG -l debug
        ;;
    scheduler)
        echo "---> Starting Scheduler"
        cd /usr/src/app/
        sleep 8
        # celery -A tasks beat &
        exec /usr/local/bin/python scheduler.py
        ;;
    queue)
        cd /usr/src/app/
        sleep 8
        exec celery -A tasks worker --concurrency=1 -Q userapp -n workerqueue
        #--loglevel=DEBUG -l debug
        ;;
    *)
        echo "Please specify argument (prod|dev) [ARGS..]";
        exit 1;
        ;;
esac

exit 0;

#!/bin/bash
set -e

export FLASK_APP=server_app.py

case "$1" in
    prod)
        echo "---> Starting in PRODUCTION mode"
        cd /usr/src/app/
        /wait-for-it.sh rabbit:5672
        /usr/local/bin/gunicorn server_app:app -w 5 -b :33405
        ;;
    dev)
        echo "---> Starting in DEV mode"
        cd /usr/src/app/
        export FLASK_DEBUG=1
        /wait-for-it.sh rabbit:5672
        flask run --port 33405  --with-threads --host '0.0.0.0'
        ;;
    scheduler)
        cd /usr/src/app/
        /wait-for-it.sh rabbit:5672
        /usr/local/bin/python scheduler.py
        ;;
    queue)
        cd /usr/src/app/
        /wait-for-it.sh rabbit:5672
        celery -A tasks worker --concurrency=1 -Q userapp --loglevel=INFO
        ;;
    reset)
        cd /usr/src/app/
        flask drop_all
        ;;
    init)
        cd /usr/src/app/
        flask init
        ;;
    set_admin_credentials)
        cd /usr/src/app/
        flask set_admin_credentials
        ;;
    *)
        echo "Please specify argument (prod|dev) [ARGS..]";
        exit 1;
        ;;

esac

exit $?;
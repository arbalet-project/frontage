#!/bin/bash
set -e

cd /usr/src/app/
/wait-for-it.sh rabbit:5672
python /usr/src/app/transmitter.py
exit $?;

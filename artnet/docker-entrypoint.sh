#!/bin/bash
set -e

cd /usr/src/app/
#/wait-for-it.sh rabbit:5672
# HACK: wait-for-it not compatible with host network mode, it will sleep 0 sec
# The fix is to sleep a while while rabbit is booting to prevent rabbitmq errors
# TODO: Get rid of Art-Net I (UDP broadcast) and clean-up network_mode: "host" in yaml
sleep 30
python /usr/src/app/transmitter.py
exit $?;

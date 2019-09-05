#!/bin/bash
set -e

/wait-for-it.sh rabbit:5672
node /home/node/live/main.js
exit $?;

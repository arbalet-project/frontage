from __future__ import print_function

import sys

from flask import request, abort


def print_flush(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def abort_doesnt_exist(obj):
    if not obj:
        abort(404, message="Object doesn't exist")

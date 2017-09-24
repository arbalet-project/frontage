"""ControlServer Script
The usage is only for debbugin & dev purpose. On production, use a reel webserver & wsgi like nginx+gunicorn ;)
And for an event faster, clean et mutli platform deployment, use Docker. Docker is nice, Docker is life.
Usage:
  control_server.py [port <port>]

Options:
  -h --help
"""
from __future__ import print_function

import sys

from server import app
from docopt import docopt
from tasks.tasks import start_scheduler

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    port = 8123 # this is the default port
    if arguments.get('port'):
        port = arguments.get('<port>')
    app.run(threaded=True, host='0.0.0.0', port=int(port))

from raven import Client
from os import environ

SENTRY = Client(environ['SENTRY_DSN'])

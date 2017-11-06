import pika, os
import logging

from scheduler_state import SchedulerState

# logging.basicConfig(level=logging.DEBUG)


CREDENTIALS = pika.PlainCredentials(os.environ.get('RABBITMQ_DEFAULT_USER'), os.environ.get('RABBITMQ_DEFAULT_PASS'))
PARAMS = pika.ConnectionParameters(  'rabbit',
                          5672,
                          '/',
                          CREDENTIALS)
RABBIT_CONNECTION = pika.BlockingConnection(PARAMS)
CHANNEL = RABBIT_CONNECTION.channel()
QUEUE_OBJ = CHANNEL.queue_declare(queue=SchedulerState.KEY_MODEL, arguments={"x-max-length":5})
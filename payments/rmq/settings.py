import os

RMQ_HOST = os.environ.get('RABBIT_HOST')
RMQ_USER = os.environ.get('RABBIT_USER')
RMQ_PASS = os.environ.get('RABBIT_PASS')

RMQ_INPUT_EXCHANGE = 'payments'
RMQ_INPUT_QUEUE = 'payment_queue'
RMQ_DEAD_EXCHANGE = 'payments_dead'
RMQ_DEAD_QUEUE = 'payments_dead_queue'
RMQ_DEAD_TTL = 1000 * 5
RETRY_COUNT = 5

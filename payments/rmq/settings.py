RMQ_HOST = 'localhost'
RMQ_INPUT_EXCHANGE = 'payments'
RMQ_INPUT_QUEUE = 'payment_queue'
RMQ_DEAD_EXCHANGE = 'payments_dead'
RMQ_DEAD_QUEUE = 'payments_dead_queue'
RMQ_DEAD_TTL = 60 * 1000 * 10
RETRY_COUNT = 2
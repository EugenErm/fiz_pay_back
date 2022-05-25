import json

import pika

from . import settings
from ...models import Payment

import logging
logger = logging.getLogger('app')


class _PaymentPublisherService:

    def __init__(self):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self._connection.channel()
        self.channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE, durable=True, )
        self.channel.queue_declare(queue=settings.RMQ_INPUT_QUEUE, durable=True,
                                   arguments={
                                       'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
                                       'x-dead-letter-routing-key': settings.RMQ_DEAD_QUEUE
                                   })

    def start_payment_event(self, payment: Payment):
        print("s " + str(payment.operation_id))
        message = bytes(json.dumps({
            "id": payment.id
        }).encode('utf-8'))

        self.channel.basic_publish(
            exchange=settings.RMQ_INPUT_EXCHANGE,
            routing_key=settings.RMQ_INPUT_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        logger.debug(f"Message << {message} >> send")



payment_publisher_service = _PaymentPublisherService()

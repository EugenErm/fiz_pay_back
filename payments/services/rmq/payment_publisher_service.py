import json

import pika

from . import settings
from ...models import Payment

import logging

logger = logging.getLogger('app')


class _PaymentPublisherService:

    def init_channel(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE, durable=True, )
        channel.queue_declare(queue=settings.RMQ_INPUT_QUEUE, durable=True,
                              arguments={
                                  'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
                                  'x-dead-letter-routing-key': settings.RMQ_DEAD_QUEUE
                              })
        return channel, connection

    def start_payment_event(self, payment: Payment):
        channel, connection = self.init_channel()
        message = bytes(json.dumps({
            "id": payment.id
        }).encode('utf-8'))

        channel.basic_publish(
            exchange="",
            routing_key=settings.RMQ_INPUT_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        logger.debug(f"Message << {message} >> send")

        connection.close()


payment_publisher_service = _PaymentPublisherService()

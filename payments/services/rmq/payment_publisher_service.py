import json

import pika

from . import settings
from ...models import Payment


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
        message = bytes(json.dumps({
            "pam": payment.card_data,
            "amount": payment.amount,
            "fio": payment.fio,
            "id": payment.id
        }).encode('utf-8'))

        message = bytes(json.dumps({
            "pam": payment.card_data,
            "amount": payment.amount,
            "fio": payment.fio,
            "id": payment.id
        }).encode('utf-8'))

        self.channel.basic_publish(
            # exchange='',
            # routing_key=settings.RMQ_INPUT_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        connection.close()


payment_publisher_service = _PaymentPublisherService()

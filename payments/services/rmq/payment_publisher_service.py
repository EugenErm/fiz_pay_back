import pika

from . import settings


class _PaymentPublisherService:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE, durable=True, )


payment_publisher_service = _PaymentPublisherService()

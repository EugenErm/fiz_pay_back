import pika

from . import settings


class _PaymentConsumerService:

    def create_consumer(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RMQ_HOST))

        channel = connection.channel()
        channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE, durable=True)
        channel.exchange_declare(exchange=settings.RMQ_DEAD_EXCHANGE, durable=True, )

        channel.queue_declare(
            queue=settings.RMQ_INPUT_QUEUE,
            durable=True,
            arguments={
                'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
                'x-dead-letter-routing-key': settings.RMQ_DEAD_QUEUE
            }
        )

        channel.queue_declare(
            queue=settings.RMQ_DEAD_QUEUE,
            durable=True,
            arguments={
                'x-message-ttl': settings.RMQ_DEAD_TTL,
                'x-dead-letter-exchange': settings.RMQ_INPUT_EXCHANGE,
                'x-dead-letter-routing-key': settings.RMQ_INPUT_QUEUE
            }
        )

        channel.queue_bind(settings.RMQ_DEAD_QUEUE, settings.RMQ_DEAD_EXCHANGE)
        channel.queue_bind(settings.RMQ_INPUT_QUEUE, settings.RMQ_INPUT_EXCHANGE)

        return channel


payment_consumer_service = _PaymentConsumerService()

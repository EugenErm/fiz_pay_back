import pika

from . import settings

# credentials = pika.PlainCredentials("fzuser", "qvAsfLxoTCmqQprmdusf")
# connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", credentials=credentials))
#

class _PaymentConsumerService:

    def create_consumer(self):
        credentials = pika.PlainCredentials(settings.RMQ_USER, settings.RMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RMQ_HOST, virtual_host='/', credentials=credentials))

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

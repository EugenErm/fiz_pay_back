import pika

from . import settings

def init_rmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=settings.RMQ_INPUT_EXCHANGE, durable=True,)

    return channel, connection

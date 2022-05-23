import time
import logging

import pika.channel

from . import payment_consumer
from . import settings

import threading

from ..models import Payment

logger = logging.getLogger(__name__)

def callback(ch: pika.channel.Channel, method, properties, body):

    print(threading.current_thread().name)

    payment = Payment.objects.get(pk=int(1540))
    print(payment)

    print(" [x] Received %r" % body.decode())
    time.sleep(1)


    if can_retry(properties):
        logger.warning('Retrying message')
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        return

    logger.error('Can`t retry, drop message')
    ch.basic_ack(delivery_tag=method.delivery_tag)

def can_retry(properties):
    """
    Заголовок x-death проставляется при прохождении сообщения через dead letter exchange.
    С его помощью можно понять, какой "круг" совершает сообщение.
    """
    deaths = (properties.headers or {}).get('x-death')
    print(properties)
    print(deaths)
    if not deaths:
        return True
    if int(deaths[0]['count']) >= settings.RETRY_COUNT:
        return False
    return True


def run_worker():
    channel = payment_consumer.init_rmq()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=callback)



    channel.start_consuming()


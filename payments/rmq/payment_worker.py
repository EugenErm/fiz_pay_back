import time

import payment_consumer
import settings

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    time.sleep(10)
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel = payment_consumer.init_rmq()

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=callback)
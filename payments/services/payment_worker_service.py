# from multiprocessing import Process
#
# from payments.models import Payment
#
import json
import threading

import pika.channel

from payments.services.rmq import settings
from payments.services.rmq.payment_consumer_service import payment_consumer_service


def start_thread_pool(task, worker_pool = 100):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=task)
        t.start()
        threads.append(t)
    return threads


# def pool_task():
#     PaymentWorker().run()





class PaymentWorker():
    def __init__(self):
        self.channel = payment_consumer_service.create_consumer()
        self.channel.basic_qos(prefetch_count=1)

    def run(self):
        print("hello")
        self.channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=self.task)
        self.channel.start_consuming()

    def task(self, ch: pika.channel.Channel, method, properties, body):
        payment_message = json.loads(body.decode())
        print(payment_message["pam"])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # def create_thread(self):
    #     t = threading.Thread(target=self.init_channel)
    #     t.start()
    #
    # def init_channel(self):
    #
    #
    # def run(self):
    #     for data in iter(self.queue.get, None):
    #
    #         pass
    #         # payment = Payment.objects.get(pk=473)
    #
    # def _init_worker_pool(self, worker_pool=10):
    #
    #     def init_worker_channel():
    #         print("init worker: " + threading.current_thread().name)
    #
    #         def cb_task(ch: pika.channel.Channel, method, properties, body):
    #             payment_message = json.loads(body.decode())
    #
    #             self.refresh_status(payment_message['id'])
    #
    #
    #             print(payment_message["pam"])
    #             ch.basic_ack(delivery_tag=method.delivery_tag)
    #             pass
    #
    #         channel = payment_consumer.init_rmq()
    #         channel.basic_qos(prefetch_count=1)
    #         channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=cb_task)
    #         channel.start_consuming()
    #
    #         print(threading.current_thread().name)



# from multiprocessing import Process
#
# from payments.models import Payment
#
import json
import threading

import pika.channel

from payments.models import Payment
from payments.services.payment_provider_sl_adapter import payment_provider_adapter
from payments.services.rmq import settings
from payments.services.rmq.payment_consumer_service import payment_consumer_service


def payment_worker():
    provider = payment_provider_adapter

    def start_payment(payment: Payment):
        print("start")
        provider.create_payout(payment)


    def payment_massage_handler(ch: pika.channel.Channel, method, properties, body):
        payment_message = json.loads(body.decode())
        payment = Payment.objects.get(pk=int(payment_message["id"]))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel = payment_consumer_service.create_consumer()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=payment_massage_handler)
    channel.start_consuming()



# class PaymentWorker():
#
#
#     def __init__(self):
#         self.channel = payment_consumer_service.create_consumer()
#         self.channel.basic_qos(prefetch_count=1)
#
#     def run(self):
#         print("hello")
#
#
#
#     def task(self,
#
#
#     # def create_thread(self):
#     #     t = threading.Thread(target=self.init_channel)
#     #     t.start()
#     #
#     # def init_channel(self):
#     #
#     #
#     # def run(self):
#     #     for data in iter(self.queue.get, None):
#     #
#     #         pass
#     #         # payment = Payment.objects.get(pk=473)
#     #
#     # def _init_worker_pool(self, worker_pool=10):
#     #
#     #     def init_worker_channel():
#     #         print("init worker: " + threading.current_thread().name)
#     #
#     #         def cb_task(ch: pika.channel.Channel, method, properties, body):
#     #             payment_message = json.loads(body.decode())
#     #
#     #             self.refresh_status(payment_message['id'])
#     #
#     #
#     #             print(payment_message["pam"])
#     #             ch.basic_ack(delivery_tag=method.delivery_tag)
#     #             pass
#     #
#     #         channel = payment_consumer.init_rmq()
#     #         channel.basic_qos(prefetch_count=1)
#     #         channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=cb_task)
#     #         channel.start_consuming()
#     #
#     #         print(threading.current_thread().name)



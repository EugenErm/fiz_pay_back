# from multiprocessing import Process
#
# from payments.models import Payment
#
import json
import threading
import pika.channel
import logging


from payments.models import Payment
from payments.services.payment_provider_sl_adapter import payment_provider_adapter
from payments.services.rmq import settings
from payments.services.rmq.payment_consumer_service import payment_consumer_service





def payment_worker():
    provider = payment_provider_adapter
    logger = logging.getLogger('app')

    logger.debug(f"Thread '{threading.current_thread().name}' started")

    def start_payment(payment: Payment):
        print(111)
        pass
        # result = provider.create_payout(payment)

    def get_payment_status(payment: Payment):
        result = provider.get_payout_by_id(payment)

    def get_payment_by_id(id: int):
        return Payment.objects.get(pk=id)



    def payment_massage_handler(ch: pika.channel.Channel, method, properties, body):
        logger.debug(f"Message << {body.decode()} >> received on thread '{threading.current_thread().name}'")
        payment_message = json.loads(body.decode())

        payment = Payment.objects.get(pk=int(payment_message["id"]))

        if payment.operation_id:
            payment.operation_id = payment.operation_id + 1
        else:
            payment.operation_id = 1
        payment.save()
        print(payment.operation_id)

        if not payment:

            ch.basic_ack(delivery_tag=method.delivery_tag)


        if not payment.operation_id:
            start_payment(payment)

    channel = payment_consumer_service.create_consumer()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=payment_massage_handler)
    channel.start_consuming()


def start_thread_pool(worker_pool=10):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=payment_worker, daemon=True)
        t.start()
        threads.append(t)
    return threads

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



# from multiprocessing import Process
#
# from payments.models import Payment
#
import json
import threading

import pika


class PaymentWorker(Process):
    def __init__(self, queue):
        super(PaymentWorker, self).__init__()
        self.queue = queue

    def run(self):
        for data in iter(self.queue.get, None):

            pass
            # payment = Payment.objects.get(pk=473)

    def _init_worker_pool(self, worker_pool=10):

        def init_worker_channel():
            print("init worker: " + threading.current_thread().name)

            def cb_task(ch: pika.channel.Channel, method, properties, body):
                payment_message = json.loads(body.decode())

                self.refresh_status(payment_message['id'])


                print(payment_message["pam"])
                ch.basic_ack(delivery_tag=method.delivery_tag)
                pass

            channel = payment_consumer.init_rmq()
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=settings.RMQ_INPUT_QUEUE, on_message_callback=cb_task)
            channel.start_consuming()

            print(threading.current_thread().name)

        for i in range(worker_pool):
            t = threading.Thread(target=init_worker_channel)
            t.start()
            self._threads.append(t)
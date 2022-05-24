import threading

from django.apps import AppConfig

from payments.services.payment_worker_service import payment_worker


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'


def start_thread_pool(task, worker_pool = 10):
    threads = []
    for i in range(worker_pool):
        t = threading.Thread(target=task)
        t.start()
        threads.append(t)
    return threads


start_thread_pool(payment_worker)

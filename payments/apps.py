import threading

from django.apps import AppConfig
from django.conf import settings


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        from payments.payment_worker import start_thread_pool
        start_thread_pool(settings.PAYMENT_WORKER_COUNT)





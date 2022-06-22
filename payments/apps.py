import threading

from django.apps import AppConfig




class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'

    def ready(self):
        from payments.services.payment_worker_service import start_thread_pool
        start_thread_pool()





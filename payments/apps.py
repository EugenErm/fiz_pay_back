from django.apps import AppConfig

from payments.services.payment_worker_service import start_thread_pool, PaymentWorker


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'


start_thread_pool(PaymentWorker().run)


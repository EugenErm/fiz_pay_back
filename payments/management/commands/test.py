from django.core.management.base import BaseCommand

from payments.services.payment_service import PaymentService


class Command(BaseCommand):


    def handle(self, *args, **options):
        PaymentService().create_payment()

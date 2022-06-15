from django.core.management.base import BaseCommand

from payments.services.payment_service import PaymentService


class Command(BaseCommand):
    service = PaymentService()

    def handle(self, *args, **options):
        # payment_id = self.service.create()
        #
        # PaymentService().start(payment_id)
        PaymentService().refresh_status(40)

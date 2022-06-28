import logging

from django.db import transaction

from .models import Payment, PaymentStatusEnum
import tasks

_logger = logging.getLogger('app')


@transaction.atomic()
def start_payment(payment: Payment) -> (bool, str):
    _logger.info(f"Start payment ID: {payment.id}, Payment: {payment}")

    if payment.status != PaymentStatusEnum.NEW:
        _logger.warning(
            f"Payment status incorrect (Payement ID: {payment.id}) status: {payment.status}")
        return False, "Incorrect payment status"

    try:
        payment.status = PaymentStatusEnum.IN_PROGRESS
        payment.save()
        _logger.info(f"Payment start status changed: {payment}")

        tasks.start_provider_payment(payment.id)
        _logger.info(f"Payment run task start_provider_payment: {payment}")
    except Exception as e:
        return False, f'{e}'



def refresh_payment_status():
    pass

def get_balance(user) -> int:
    pass

def _get_active_cert():
    pass
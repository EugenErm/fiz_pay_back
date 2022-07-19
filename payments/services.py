import logging

from django.contrib.auth.models import User
from django.db import transaction

from .exceptions import IncorrectPaymentStatusException
from .mappers import payment_state_mapper
from .models import Payment, PaymentStatusEnum
from .rmq.payment_publisher_service import payment_publisher_service
from .sl_payment_service import start_provider_payment, get_provider_balance, get_provider_payment
from .types import ProviderPayment

_logger = logging.getLogger('app')


def start_payment(payment: Payment):
    _logger.info(f"PaymentServices > start_payment -- payment id: {payment.id} -- Start payment: {payment}")

    if payment.status != PaymentStatusEnum.NEW:
        _logger.warning(
            f"PaymentServices > start_payment -- payment id: {payment.id} -- Error Payment status incorrect status: {payment.status}")
        raise IncorrectPaymentStatusException(f"Incorrect payment status - current status is {payment.status}")

    payment.status = PaymentStatusEnum.IN_PROGRESS
    payment.save()
    _logger.info(f"PaymentServices > start_payment -- payment id: {payment.id} -- Payment start status changed: {payment}")

    payment_publisher_service.start_payment_event(payment)

def start_payments_by_ids(ids: [int]):
    payments = Payment.objects.filter(pk__in=ids)
    for payment in payments:
        start_payment(payment)


def get_balance(user: User) -> int:
    _logger.info(f"Payment services -- get_balance for user_id: {user.id}")

    balance = get_provider_balance(user)

    _logger.info(f"Payment services -- get_balance for user_id: {user.id} result {balance} ")
    return balance


def refresh_payment(payment: Payment):
    _logger.info(f"PaymentServices > refresh_payment -- payment id: {payment.id} -- Start refresh payment: {payment}")
    provider_payment = get_provider_payment(payment)

    _logger.info(f"PaymentServices > refresh_payment -- payment id: {payment.id} -- receive provider payment {provider_payment}")
    refresh_payment_from_provider_payment(payment, provider_payment)


def refresh_payment_from_provider_payment(payment: Payment, provider_payment: ProviderPayment):
    _logger.info(f"PaymentServices > refresh_payment_from_provider_payment -- payment id: {payment.id} -- provider_payment: {provider_payment}")

    payment.final = provider_payment.final
    payment.status_message = payment_state_mapper(provider_payment.state, provider_payment.substate,  provider_payment.code)

    if provider_payment.state == '60':
        payment.status = PaymentStatusEnum.SUCCESS

    if provider_payment.state == '80' or provider_payment.state == '-2':
        payment.status = PaymentStatusEnum.ERROR

    if provider_payment.trans is not None:
        payment.operation_id = provider_payment.trans

    if provider_payment.provider_error_text is not None:
        payment.provide_error_text = provider_payment.provider_error_text

    if provider_payment.server_time is not None:
        payment.start_payment_time = provider_payment.server_time

    if provider_payment.process_time is not None:
        payment.process_payment_time = provider_payment.process_time

    payment.save()
    _logger.info(f"PaymentServices > refresh_payment_from_provider_payment -- payment id: {payment.id} -- Payment saved: {payment}")



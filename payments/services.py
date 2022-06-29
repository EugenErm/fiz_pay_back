from typing import Optional

import logging

from django.db import transaction
from django.contrib.auth.models import User


from paymentcert.models import PaymentCert
from paymentcert.services import get_active_cert
from .exceptions import IncorrectPaymentStatusException, ProviderPaymentNotFoundException
from .mappers import payment_state_mapper

from .sl_payment_service import SLPaymentClient
from .models import Payment, PaymentStatusEnum
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



def get_balance(user: User) -> int:
    _logger.info(f"Payment services -- get_balance for user_id: {user.id}")

    client = _get_payment_client_by_user_id(user.id)
    balance = client.get_balance()

    _logger.info(f"Payment services -- get_balance for user_id: {user.id} result {balance} ")
    return balance['amount']


def _start_provider_payment(payment: Payment):
    _logger.info(
        f"PaymentServices > start_provider_payment -- payment id: {payment.id} -- Start init payment: {payment}")

    client = _get_payment_client_by_user_id(payment.user_id)
    provider_payment = client.create_provider_payment(payment)
    _logger.info(
        f"PaymentServices > start_provider_payment -- payment id: {payment.id} -- Provider payment started:  {provider_payment}")

    return provider_payment


def _get_provider_payment(payment: Payment) -> Optional[ProviderPayment]:
    _logger.info(f"PaymentServices > refresh_payment -- payment id: {payment.id} -- Start refresh payment: {payment}")

    client = _get_payment_client_by_user_id(payment.user_id)
    provider_payment = client.get_payment_by_id(payment)

    if provider_payment.state == '-2':
        _logger.warning( f"PaymentClient > get_payout_by_id -- payment id: {payment.id}; provider payment not found")
        return None

    _logger.info(
        f"PaymentServices > refresh_payment -- payment id: {payment.id} -- Provider payment received:  {provider_payment}")
    return provider_payment


def _refresh_payment_from_provider_payment(payment: Payment, provider_payment: ProviderPayment):
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


def _get_payment_client_by_user_id(user_id) -> SLPaymentClient:
    cert = get_active_cert(user_id=user_id)
    return SLPaymentClient(cert=cert)




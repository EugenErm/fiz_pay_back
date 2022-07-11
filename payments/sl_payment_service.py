from typing import Optional

import logging

from django.contrib.auth.models import User
from paymentcert.services import get_active_cert
from .exceptions import InvalidPaymentCertException

from .models import Payment
from .sl_payment_client import SLPaymentClient
from .types import ProviderPayment

_logger = logging.getLogger('app')


def start_provider_payment(payment: Payment):
    _logger.info(
        f"PaymentServices > start_provider_payment -- payment id: {payment.id} -- Start init payment: {payment}")

    client = _get_payment_client_by_user_id(payment.user_id)
    provider_payment = client.create_provider_payment(payment)
    _logger.info(
        f"PaymentServices > start_provider_payment -- payment id: {payment.id} -- Provider payment started:  {provider_payment}")

    return provider_payment


def get_provider_payment(payment: Payment) -> Optional[ProviderPayment]:
    _logger.info(f"Payment sl > get_provider_payment -- payment id: {payment.id}")

    client = _get_payment_client_by_user_id(payment.user_id)
    provider_payment = client.get_payment_by_id(payment)

    if provider_payment.state == '-2':
        _logger.warning(f"Payment sl > get_provider_payment  -- payment id: {payment.id}; provider payment not found")
        return None

    _logger.info(
        f"Payment sl > get_provider_payment  -- payment id: {payment.id} -- Provider payment received:  {provider_payment}")
    return provider_payment


def get_provider_balance(user: User) -> int:
    _logger.info(f"Payment sl services -- get_balance for user_id: {user.id}")

    client = _get_payment_client_by_user_id(user.id)
    balance = client.get_balance()

    _logger.info(f"Payment sl services -- get_balance for user_id: {user.id} result {balance} ")
    return balance['amount']


def _get_payment_client_by_user_id(user_id) -> SLPaymentClient:
    cert = get_active_cert(user_id=user_id)
    if not cert:
        raise InvalidPaymentCertException('Payment cert not fount')

    return SLPaymentClient(cert=cert)

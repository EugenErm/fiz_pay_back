import logging

from django.db import transaction

from payments.dto.create_payment_dto import CreatePaymentDto
from payments.exceptions.incorrect_payment_status_exception import IncorrectPaymentStatusException
from payments.exceptions.payment_not_fount_exception import PaymentNotFountException
from payments.models import Payment, PaymentStatusEnum
from payments.services.payment_provider_sl_adapter import payment_provider_adapter
from payments.services.rmq.payment_publisher_service import payment_publisher_service
from utils.payment_state_mapper import payment_state_mapper


class _BalanceService:

    def __init__(self):
        self.payment_provider_adapter = payment_provider_adapter
        self.logger = logging.getLogger('app')

    def get_balance(self):
        return self.payment_provider_adapter.get_balance()


balance_service = _BalanceService()

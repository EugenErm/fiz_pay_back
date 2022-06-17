import logging

from django.db import transaction

from payments.dto.create_payment_dto import CreatePaymentDto
from payments.exceptions.incorrect_payment_status_exception import IncorrectPaymentStatusException
from payments.exceptions.payment_not_fount_exception import PaymentNotFountException
from payments.models import Payment, PaymentStatusEnum
from payments.services.rmq.payment_publisher_service import payment_publisher_service
from utils.payment_state_mapper import payment_state_mapper


class _PaymentService:

    def __init__(self):
        self.payment_model = Payment
        self.payment_publisher_service = payment_publisher_service
        self.logger = logging.getLogger('app')

    def get_payment_by_id(self, payment_id: int):
        return self.payment_model.objects.get(pk=payment_id)

    def create_payment(self, create_payment_dto: CreatePaymentDto) -> Payment:
        fio = f"{create_payment_dto.last_name} {create_payment_dto.name}"
        if create_payment_dto.middle_name:
            fio += f" {create_payment_dto.middle_name}"
        payment = self.payment_model(
            fio=fio,
            card_data=create_payment_dto.pam,
            amount=create_payment_dto.amount,
            user_id=1)
        payment.save()

        return payment

    def is_payment_exist(self, payment_id: int) -> bool:
        return bool(self.get_payment_by_id(payment_id))

    @transaction.atomic()
    def start_payment(self, payment_id: int):
        self.logger.debug(f"_PaymentService start_payment ID: {payment_id}")
        payment = self.get_payment_by_id(payment_id)
        self.logger.debug(f"_PaymentService Find payment: {payment}")
        if not payment:
            raise PaymentNotFountException()

        if payment.status != PaymentStatusEnum.NEW:
            self.logger.error(f"_PaymentService Payment status incorrect (Payement ID: {payment.id}) status: {payment.status}")
            raise IncorrectPaymentStatusException()

        payment.status = PaymentStatusEnum.IN_PROGRESS
        payment.save()

        self.payment_publisher_service.start_payment_event(payment)

    def get_payment_list(self):
        payments = self.payment_model.objects.all()
        return payments

    def clear_payment_list(self):
        self.payment_model.objects.all().delete()

    @transaction.atomic()
    def refresh_payment_status_from_provider_payment(self, payment_id: int, provider_payment):
        self.logger.debug(f"_PaymentService refresh_payment_status_from_provider_payment payment ID: {payment_id}; provider_payment: {provider_payment}")
        payment = Payment.objects.get(pk=payment_id)

        if provider_payment.get("trans"):
            payment.operation_id = provider_payment['trans']

        if provider_payment.get("provider-error-text"):
            payment.provide_error_text = provider_payment['provider-error-text']

        if provider_payment.get("server_time"):
            payment.start_payment_time = provider_payment['server_time']

        if provider_payment.get("process_time"):
            payment.process_payment_time = provider_payment['process_time']

        if provider_payment.get("final"):
            payment.final = provider_payment['final']

        if provider_payment.get("state") and provider_payment.get("substate") and provider_payment.get("code"):
            payment.status_message = payment_state_mapper(provider_payment['state'], provider_payment['substate'],  provider_payment['code'])

        if provider_payment.get("state") == '60':
            payment.status = PaymentStatusEnum.SUCCESS

        if provider_payment.get("state") == '80' or provider_payment.get("state") == '-2':
            payment.status = PaymentStatusEnum.ERROR

        from django.forms.models import model_to_dict
        # print(model_to_dict(payment))
        payment.save()


payment_service = _PaymentService()

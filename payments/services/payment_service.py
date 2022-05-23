from django.db import transaction

from payments.dto.create_payment_dto import CreatePaymentDto
from payments.exceptions.incorrect_payment_status_exception import IncorrectPaymentStatusException
from payments.exceptions.payment_not_fount_exception import PaymentNotFountException
from payments.models import Payment, PaymentStatusEnum


class _PaymentService:

    def __init__(self):
        self.payment_model = Payment

    def get_payment_by_id(self, payment_id: int):
        return self.payment_model.objects.get(pk=payment_id)

    def create_payment(self, create_payment_dto: CreatePaymentDto) -> Payment:
        fio = f"{create_payment_dto.last_name} {create_payment_dto.name}"
        if create_payment_dto.middle_name:
            fio += f" {create_payment_dto.middle_name}"
        payment = self.payment_model(fio=fio, card_data=create_payment_dto.pam, amount=create_payment_dto.amount)
        payment.save()
        print(payment)
        return payment

    def is_payment_exist(self, payment_id: int) -> bool:
        return bool(self.get_payment_by_id(payment_id))

    @transaction.atomic()
    def start_payment(self, payment_id: int):
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            raise PaymentNotFountException()

        if payment.status == PaymentStatusEnum.NEW:
            raise IncorrectPaymentStatusException()

        self._add_payment_to_rabbit(payment)
        payment.status = PaymentStatusEnum.IN_PROGRESS
        payment.save()

        #     self._add_payment_to_rabbit(payment)
        #     payment.status = PaymentStatusEnum.IN_PROGRESS
        #     payment.save()

    def get_payment_list(self) -> list:
        payments = list(self.payment_model.objects.all().values())
        return payments

    def clear_payment_list(self):
        self.payment_model.objects.all().delete()

    @transaction.atomic()
    def start_payment_by_id(self, id: int):
        payment = Payment.objects.get(pk=int(id))
        self._add_payment_to_rabbit(payment)
        # if payment and payment.status == PaymentStatusEnum.NEW:
        #     self._add_payment_to_rabbit(payment)
        #     payment.status = PaymentStatusEnum.IN_PROGRESS
        #     payment.save()

    @transaction.atomic()
    def refresh_status(self, payment_id: int):
        payment = Payment.objects.get(pk=payment_id)
        trans = self.provider.get_payout_by_id(payment.id)

        payment.operation_id = trans['trans']

        payment.status_message = self._parce_state(trans['state'], trans['substate'])

        if trans['final'] == '1':
            payment.status = PaymentStatusEnum.SUCCESS

        if trans.get('provider-error-text'):
            payment.provide_error_text = trans.get('provider-error-text')

        payment.save()

        return trans

    def get_payment_info(self, id):
        pass


payment_service = _PaymentService()

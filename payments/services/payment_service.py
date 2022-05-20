import asyncio
import json
from asyncio import Queue

import pandas
import pika
from django.db import transaction

from payments.models import Payment, PaymentStatusEnum
from payments.rmq import payment_publisher
from payments.services.payment_provider_sl_adapter import PaymentProviderSlAdapter
from utils.validators import is_credit_card


class PaymentService:
    provider = PaymentProviderSlAdapter(point='274')

    def get_balance(self):
        print(self.provider.get_balance())

    def create(self, payment):
        fio = f"{payment['lastname']} {payment['name']}"
        if payment.notna().get('middlename'):
            fio += f" {payment['middlename']}"

        payment = Payment(fio=fio, card_data=payment['pam'], amount=payment['amount'])
        payment.save()
        print(payment)
        return payment.id

    def import_payments_from_file(self, payments: pandas.DataFrame):
        ### Validate ###
        if len(payments) > 1000:
            raise Exception("Count > 1000")
        file_errors = []
        for index, payment in payments.iterrows():
            errors = validate_payment(payment)
            if not len(errors) == 0:
                file_errors.append((index, errors))
        if not len(file_errors) == 0:
            raise Exception(file_errors)
        ######

        ### Create payment ###
        for index, payment in payments.iterrows():
            self.create(payment)
        ######

    def start_payment_by_ids(self, payment_ids: [int]):
        for id in payment_ids:
            self.start_payment_by_id(id)

    @transaction.atomic()
    def start_payment_by_id(self, id: int):
        payment = Payment.objects.get(pk=int(id))
        if payment and payment.status == PaymentStatusEnum.NEW:
            self._add_payment_to_rabbit(payment)
            payment.status = PaymentStatusEnum.IN_PROGRESS
            payment.save()

    def _add_payment_to_rabbit(self, payment):
        channel, connection = payment_publisher.init_rmq()


        channel.queue_declare(queue='payment_queue', durable=True)

        message = bytes(json.dumps({
            "pam": payment.card_data,
            "amount": payment.amount,
            "fio": payment.fio,
            "id": payment.id
        }).encode('utf-8'))

        channel.basic_publish(
            exchange='',
            routing_key='payment_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

        connection.close()

    @transaction.atomic()
    def refresh_status(self, payment_id: int):
        payment = Payment.objects.get(pk=payment_id)
        trans = self.provider.get_payout_by_id(payment.id)

        payment.operation_id = trans['trans']

        payment.status_message = parce_state(trans['state'], trans['substate'])

        if trans['final'] == '1':
            payment.status = PaymentStatusEnum.SUCCESS

        if trans.get('provider-error-text'):
            payment.provide_error_text = trans.get('provider-error-text')

        payment.save()

    def get_payment_list(self) -> list:
        payments = list(Payment.objects.all().values())
        return payments

    def clear_payment_list(self):
        Payment.objects.all().delete()

    def get_payment_info(self, id):
        pass


def validate_payment(payment: pandas.Series) -> list:
    payment_na = payment.notna()
    errors = []
    if not payment_na.get('pam'):
        errors.append(f"pam is required")
    elif not is_credit_card(payment['pam']):
        errors.append(f"{payment['pam']} is not credit card")

    if not payment_na.get('name'):
        errors.append(f"name is required")

    if not payment_na.get('lastname'):
        errors.append(f"lastname is required")

    if not payment_na.get('amount'):
        errors.append(f"amount is required")
    else:
        try:
            int(payment['amount'])
        except:
            errors.append(f"amount err: {payment['amount']} is not int")

    return errors


def parce_state(state, sub_state):
    if state == '0':
        if sub_state == '0':
            return 'Новый'
        if sub_state == '1':
            return 'Готов к обработке'
        if sub_state == '2':
            return 'Определение провайдера'
        if sub_state == '3' or sub_state == '4':
            return 'Fraud-control'
        if sub_state == '5':
            return 'Подтверждение'
        if sub_state == '6':
            return 'Провайдер не задан'
        if sub_state == '7':
            return 'Таймаут'
        if sub_state == '8':
            return 'Отложен'
        if sub_state == '9':
            return 'Ожидает подтверждения'
        if sub_state == '11':
            return 'Вознаграждение не задано'

    if state == '10':
        return "Платеж заблокирован"

    if state == '20':
        if sub_state == '1':
            return 'Готов к списанию'
        if sub_state == '2' or sub_state == '3':
            return 'Списание средств со счета'
        if sub_state == '4':
            return 'Недостаточно средств на счете'

    if state == '30':
        if sub_state == '1':
            return 'Готов к предварительной верификации'
        if sub_state == '2':
            return 'Предварительная верификация, в обработке'
        if sub_state == '3':
            return 'Верификация закончилась неоднозначной ошибкой'
        if sub_state == '4':
            return 'Не прошла проверку модулем предварительной проверки'

    if state == '40':
        if sub_state == '1':
            return 'Готов к проведению'
        if sub_state == '2' or sub_state == '3':
            return 'Проведение'
        if sub_state in ['4', '5', '6', '7']:
            return 'Ошибка проведения'
        if sub_state == '8':
            return 'Ожидается ответ от внешнего поставщика'
        if sub_state == '9':
            return 'Ожидание подтверждения от внешней системы'

    if state == '60':
        return "Статус успешного проведения (финальный)"

    if state == '80':
        if sub_state in ['1', '2', '3']:
            return 'Платеж отменен вручную'
        if sub_state == '4':
            return 'Недостаточно средств на счете'
        if sub_state == '5':
            return 'Ошибка проведения'
        if sub_state in ['6', '7', '8']:
            return 'Другая ошибка'
        if sub_state == '9':
            return 'Возврат средств'

    return f"Неизвестная ошибка st: {state}; subst: {sub_state}"

import threading

import json
import pandas
import pika
from django.db import transaction

from payments.models import Payment, PaymentStatusEnum
from payments.rmq import payment_publisher, payment_consumer, settings

from payments.services.payment_provider_sl_adapter import PaymentProviderSlAdapter
from utils.validators import is_credit_card





class _PaymentService:

    def __init__(self):
        self.payment_model = Payment

    def get_payment_by_id(self, payment_id: int):
        return self.payment_model.objects.get(pk=payment_id)

    def create_payment(self, payment):


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
        if len(payments) > 10000:
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
        self._add_payment_to_rabbit(payment)
        # if payment and payment.status == PaymentStatusEnum.NEW:
        #     self._add_payment_to_rabbit(payment)
        #     payment.status = PaymentStatusEnum.IN_PROGRESS
        #     payment.save()

    def _add_payment_to_rabbit(self, payment):
        channel, connection = payment_publisher.init_rmq()

        channel.queue_declare(queue='payment_queue', durable=True,
                              arguments={
                                  'x-dead-letter-exchange': settings.RMQ_DEAD_EXCHANGE,
                                  'x-dead-letter-routing-key': settings.RMQ_DEAD_QUEUE
                              })

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

        payment.status_message = self._parce_state(trans['state'], trans['substate'])

        if trans['final'] == '1':
            payment.status = PaymentStatusEnum.SUCCESS

        if trans.get('provider-error-text'):
            payment.provide_error_text = trans.get('provider-error-text')

        payment.save()

        return trans

    def get_payment_list(self) -> list:
        payments = list(Payment.objects.all().values())
        return payments

    def clear_payment_list(self):
        Payment.objects.all().delete()

    def get_payment_info(self, id):
        pass






payment_service = _PaymentService()
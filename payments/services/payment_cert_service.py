import logging

from django.db import transaction

from payments.dto.create_payment_dto import CreatePaymentDto
from payments.exceptions.incorrect_payment_status_exception import IncorrectPaymentStatusException
from payments.exceptions.payment_not_fount_exception import PaymentNotFountException
from payments.models import Payment, PaymentStatusEnum, PaymentCert
from payments.services.rmq.payment_publisher_service import payment_publisher_service
from utils.payment_state_mapper import payment_state_mapper


class _PaymentCertService:

    def __init__(self):
        self.payment_cert_model = PaymentCert

    def load_cert(self, point, name, password, cert_file):
        payment_cert = self.payment_cert_model(
            point=point,
            name=name,
            password=password,
            p12cert=cert_file
        )
        payment_cert.save()

    def get_last_cert(self) -> PaymentCert:
        return self.payment_cert_model.objects.last()


payment_cert_service = _PaymentCertService()

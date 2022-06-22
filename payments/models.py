import logging
from django.db import models, transaction
from django.contrib.auth.models import User

from .exceptions import IncorrectPaymentStatusException
from .tasks import start_payment
from .validators import is_credit_card_validator

_logger = logging.getLogger('app')


class PaymentStatusEnum(models.TextChoices):
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'


class Payment(models.Model):
    operation_id = models.IntegerField(null=True)

    start_payment_time = models.CharField(max_length=40, null=True)
    process_payment_time = models.CharField(max_length=40, null=True)

    final = models.CharField(max_length=20, null=True)
    status_message = models.TextField(default='')
    provide_error_text = models.TextField(default='')

    # ---
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices, default=PaymentStatusEnum.NEW)

    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default='-')
    middle_name = models.CharField(max_length=100, null=True)

    card_data = models.CharField(max_length=20, validators=[is_credit_card_validator])
    amount = models.IntegerField()
    metadata = models.TextField(default='0')

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transaction.atomic()
    def start(self):
        _logger.debug(f"Start payment ID: {self.id}")
        _logger.debug(f"Find payment: {self}")

        if self.status != PaymentStatusEnum.NEW:
            _logger.error(
                f"Payment status incorrect (Payement ID: {self.id}) status: {self.status}")
            raise IncorrectPaymentStatusException()

        self.status = PaymentStatusEnum.IN_PROGRESS
        self.save()
        start_payment(self.id)
        _logger.debug(f"Payment started: {self}")


    def __str__(self):
        return f"Payment(" \
               f" id: {self.pk};" \
               f" trans: {self.operation_id};" \
               f" status: {self.status};" \
               f" final: {self.final};" \
               f" status_message: {self.status_message};" \
               f" provide_error_text: {self.provide_error_text};" \
               f" amount:{self.amount})"

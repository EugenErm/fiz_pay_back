from django.db import models
from django.contrib.auth.models import User


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

    fio = models.CharField(max_length=150)
    card_data = models.CharField(max_length=150)
    amount = models.IntegerField()
    metadata = models.TextField(default='0')

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment(" \
               f" id: {self.pk};" \
               f" trans: {self.operation_id};" \
               f" status: {self.status};" \
               f" final: {self.final};" \
               f" status_message: {self.status_message};" \
               f" provide_error_text: {self.provide_error_text};" \
               f" amount:{self.amount})"

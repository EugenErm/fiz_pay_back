from django.db import models


class Payment(models.Model):
    class PaymentStatusEnum(models.TextChoices):
        NEW = 'NEW'
        IN_PROGRESS = 'IN_PROGRESS'
        SUCCESS = 'SUCCESS'
        ERROR = 'ERROR'

    operation_id = models.IntegerField(null=True)
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices, default=PaymentStatusEnum.NEW)
    error_code = models.IntegerField(default=0)
    error_description = models.TextField(default='')

    fio = models.CharField(max_length=150)
    card_data = models.CharField(max_length=150)
    amount = models.IntegerField()
    metadata = models.TextField(default='0')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

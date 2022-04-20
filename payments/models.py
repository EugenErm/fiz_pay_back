from django.db import models


class Payment(models.Model):
    class PaymentStatusEnum(models.TextChoices):
        NEW = 'NEW'
        IN_PROGRESS = 'IN_PROGRESS'
        SUCCESS = 'SUCCESS'
        ERROR = 'ERROR'

    operation_id = models.IntegerField(blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices)
    error_code = models.IntegerField(default=0)
    error_description = models.TextField()

    fio = models.CharField(max_length=150, primary_key=True, unique=True)
    card_data = models.CharField(max_length=150)
    amount = models.IntegerField()
    metadata = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

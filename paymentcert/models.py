from django.db import models
from django.contrib.auth.models import User


class PaymentCert(models.Model):

    point = models.CharField(max_length=10, blank=False)
    name = models.CharField(max_length=50, blank=False)
    password = models.CharField(max_length=50, blank=False)
    p12cert = models.FileField(upload_to='certificates/', blank=False)

    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PaymentCert(" \
               f" id: {self.pk};" \
               f" name: {self.name};" \
               f" point:{self.point})"


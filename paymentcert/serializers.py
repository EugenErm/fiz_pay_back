from rest_framework import serializers

from .models import PaymentCert


class PaymentCertCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PaymentCert
        fields = ['name', 'password', 'point', 'user', 'p12cert']


class PaymentCertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCert
        fields = ['id', 'name', 'point']


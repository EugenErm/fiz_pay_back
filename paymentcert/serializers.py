from rest_framework import serializers
from .models import PaymentCert


class P12Field(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data.read()


class PaymentCertCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    p12cert = P12Field()

    class Meta:
        model = PaymentCert
        fields = ['name', 'password', 'point', 'user', 'p12cert']


class PaymentCertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCert
        fields = ['id', 'name', 'point', 'user']


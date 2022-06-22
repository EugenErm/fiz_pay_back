from rest_framework import serializers

from .models import Payment


class PaymentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Payment
        fields = ["id", "name", "last_name", "middle_name", "card_data", "amount", 'user']


class PaymentListSerializer(serializers.ModelSerializer):
    card_data = serializers.SerializerMethodField()

    def get_card_data(self, obj):
        return obj.card_data[-4:]

    class Meta:
        model = Payment
        fields = "__all__"


# class PaymentsStartSerializer(serializers.Serializer):
#     ids = serializers.ListField(child=serializers.IntegerField(min_value=0, max_value=100))

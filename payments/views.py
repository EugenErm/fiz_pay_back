from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import InvalidPaymentCertException, IncorrectPaymentStatusException
from .models import Payment
from .permissions import IsAdminOrIsSelf
from .serializers import PaymentCreateSerializer, PaymentListSerializer
from .services import refresh_payment, start_payment, get_balance


class PaymentsViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer

        return PaymentListSerializer

    @action(methods=['post'], detail=True, permission_classes=[IsAdminOrIsSelf])
    def start(self, request, pk=None):
        instance = self.get_object()
        try:
            start_payment(instance)
            return Response({'status': 'ok'})

        except IncorrectPaymentStatusException as e:
            return Response({'status': 'err', 'message': str(e)})
        except InvalidPaymentCertException as e:
            return Response({'status': 'err', 'message': str(e)})

    @action(methods=['post'], detail=True, permission_classes=[IsAdminOrIsSelf])
    def refresh(self, request, pk=None):
        instance = self.get_object()
        try:
            refresh_payment(instance)
            return Response({'status': 'ok'})

        except IncorrectPaymentStatusException as e:
            return Response({'status': 'err', 'message': str(e)})
        except InvalidPaymentCertException as e:
            return Response({'status': 'err', 'message': str(e)})


class BalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            balance = get_balance(request.user)
            print(balance)
            return Response({'status': 'ok', 'balance': balance})

        except InvalidPaymentCertException as e:
            return Response({'status': 'err', 'message': str(e)})



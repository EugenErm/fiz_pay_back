from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .permissions import IsAdminOrIsSelf
from .serializers import PaymentCreateSerializer, PaymentListSerializer
from .services import start_payment, get_balance


class PaymentsViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED, headers=headers)

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer

        return PaymentListSerializer

    @action(methods=['post'], detail=True, permission_classes=[IsAdminOrIsSelf])
    def start(self, request):
        instance = self.get_object()
        result = start_payment(instance)
        if result:
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'err'})


class BalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        balance = get_balance(user)

        usernames = [user.username for user in User.objects.all()]
        return Response({'status': 'ok', 'balance': balance})

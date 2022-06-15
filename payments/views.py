from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated,
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Payment
# from .permissions import IsAdminOrIsSelf
from .serializers import PaymentCreateSerializer, PaymentListSerializer, PaymentsStartSerializer


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

    @action(methods=['post'], detail=False, permission_classes=[IsAdminOrIsSelf])
    def start(self, request):
        serializer = PaymentsStartSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


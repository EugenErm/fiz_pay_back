from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PaymentCert
from .serializers import PaymentCertListSerializer, PaymentCertCreateSerializer
from .services import get_active_cert, check_cert


class PaymentCertViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    queryset = PaymentCert.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_obj = serializer.save()
        try:
            check_cert(model_obj)
            headers = self.get_success_headers(serializer.data)
            return Response({"status": "ok"}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            model_obj.delete()
            return Response({"status": "err", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCertCreateSerializer

        return PaymentCertListSerializer

    @action(methods=['get'], detail=False)
    def active(self, request):
        paymentcert = get_active_cert(request.user)
        if paymentcert:
            serializer = self.get_serializer(paymentcert)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "err"}, status=status.HTTP_404_NOT_FOUND)

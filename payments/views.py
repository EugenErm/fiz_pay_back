from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .paginations import StandardResultsSetPagination
from .payment_import_service import import_payments_from_file
from .exceptions import InvalidPaymentCertException, IncorrectPaymentStatusException, ImportCountLimitException
from .forms import UploadPaymentRegisterForm
from .models import Payment
from .permissions import IsAdminOrIsSelf
from .serializers import PaymentCreateSerializer, PaymentListSerializer, StartPaymentsSerializer
from .services import refresh_payment, start_payment, get_balance, start_payments_by_ids


class PaymentsViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    queryset = Payment.objects.all().order_by("-pk")
    permission_classes = [IsAdminOrIsSelf]
    pagination_class = StandardResultsSetPagination

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)


    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminOrIsSelf]
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer

        return PaymentListSerializer

    @action(methods=['post'], url_path=r'import', detail=False)
    def import_payment(self, request):
        if request.method == 'POST':
            upload_form = UploadPaymentRegisterForm(request.POST, request.FILES)
            if upload_form.is_valid():
                try:
                    errors, payments = import_payments_from_file(upload_form.files['file'], user=request.user)

                    if len(errors) != 0:
                        return Response({
                            "status": "ok",
                            "data": {
                                "status": 'err',
                                "errorType": 'validation',
                                "errorList": errors
                            }
                        })

                    serializer = self.get_serializer_class()

                    return Response({
                        "status": "ok",
                        "data": {
                            "status": 'success',
                            "payments": serializer(payments, many=True).data
                        }
                    })

                except ImportCountLimitException as e:
                    return Response({
                        "status": "ok",
                        "data": {
                            "status": 'err',
                            "errorType": 'limits',
                            "message": "Превышено максимальное количество платежей"
                        }
                    })
                except Exception as e:
                    return Response({
                        "status": "err",
                        "message": "Неизвестная ошибка",
                        "data": e
                    })
            else:
                return Response({
                        "status": "err",
                        "message": "Ошибка отправки формы",
                        "data": upload_form.errors
                    })

    @action(methods=['post'], detail=True)
    def start(self, request, pk=None):
        instance = self.get_object()
        try:
            start_payment(instance)
            return Response({'status': 'ok'})

        except IncorrectPaymentStatusException as e:
            return Response({'status': 'err', 'message': str(e)})
        except InvalidPaymentCertException as e:
            return Response({'status': 'err', 'message': str(e)})

    @action(methods=['post'], detail=False, url_path=r'start')
    def start_by_ids(self, request):
        serializer = StartPaymentsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_payments_by_ids(serializer.data)

        return Response({'status': 'err', 'message': "str(e)"})


    @action(methods=['post'], detail=True)
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
            return Response({'status': 'ok', 'balance': balance})

        except InvalidPaymentCertException as e:
            return Response({'status': 'err', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)



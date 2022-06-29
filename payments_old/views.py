import json

from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from utils.validators.is_credit_card_validator import is_credit_card
from .dto.create_payment_dto import CreatePaymentDto
from .forms import UploadPaymentRegisterForm, UploadCertForm
from .services.balance_service import balance_service
from .services.payment_cert_service import payment_cert_service
from .services.payment_import_service import payment_import_service
from .services.payment_service import payment_service


# Payments Cert

# @csrf_exempt
# def upload_cert(request):
#     if request.method == 'POST':
#         upload_form = UploadCertForm(request.POST, request.FILES)
#         print(upload_form.data)
#
#         payment_cert_service.load_cert(
#             point=upload_form.data['point'],
#             name=upload_form.data['name'],
#             password=upload_form.data['password'],
#             cert_file=upload_form.files['file'])
#
#         return JsonResponse(
#             {
#                 "status": "ok"
#             }
#         )


@csrf_exempt
def get_active_certificate(request):
    if request.method == 'GET':
        active_cert = payment_cert_service.get_last_cert()

        if active_cert:
            return JsonResponse(
                {
                    "status": "ok",
                    "data": model_to_dict(active_cert, ['id', 'name', 'point']),
                }
            )
        else:
            return JsonResponse(
                {
                    "status": "ok",
                    "data": None,
                }
            )


# Payments

@csrf_exempt
def upload_payment_list_file(request):
    if request.method == 'POST':
        upload_form = UploadPaymentRegisterForm(request.POST, request.FILES)
        if upload_form.is_valid():
            try:
                payments_pandas = payment_import_service.import_payments_from_file(upload_form.files['file'])

                if not payment_import_service.validate_limits(payments_pandas):
                    return JsonResponse({
                        "status": "ok",
                        "data": {
                            "status": 'err',
                            "errorType": 'limits',
                            "message": "Превышено максимальное количество платежей"
                        }
                    })

                errors = payment_import_service.validate_payments(payments_pandas)
                if len(errors) != 0:
                    return JsonResponse({
                        "status": "ok",
                        "data": {
                            "status": 'err',
                            "errorType": 'validation',
                            "errorList": errors
                        }
                    })

                created_payments = payment_import_service.create(payments_pandas)
                return JsonResponse({
                    "status": "ok",
                    "data": {
                        "status": 'success',
                        "payments": list(map(lambda payment: model_to_dict(payment), created_payments))
                    }
                })

            except Exception as e:
                return JsonResponse({
                    "status": "err",
                    "message": "Неизвестная ошибка",
                    "data": e
                })

        return JsonResponse(
            {
                "status": "err",
                "message": "Ошибка отправки формы",
                "data": upload_form.errors
            }
        )


@csrf_exempt
def payments(request):
    if request.method == 'POST':
        return create_payment(request)
    if request.method == "GET":
        return get_payment_list(request)


@csrf_exempt
def create_payment(request):
    create_payment_dto = CreatePaymentDto.parse_raw(request.body)

    if not is_credit_card(create_payment_dto.pam):
        return JsonResponse({"status": "err", "message": "Проверьте номер карты"})

    payment = payment_service.create_payment(create_payment_dto)
    return JsonResponse({
        "status": "ok",
        "data": model_to_dict(payment)
    })


@csrf_exempt
def get_payment_list(request):
    page_size = (request.GET.get("pageSize") or 20)
    page_index = (request.GET.get("pageIndex") or 0)

    payments = payment_service.get_payment_list().order_by("-pk")
    paginator = Paginator(payments, page_size)
    page = paginator.page(int(page_index) + 1)

    return JsonResponse(
        {
            "data": list(page.object_list.values()),
            "totalCount": paginator.count
        }
    )


@csrf_exempt
def get_payment_by_id(request, payment_id: int):
    payment = payment_service.get_payment_by_id(payment_id)
    return JsonResponse({
        "status": "ok",
        "data": model_to_dict(payment)
    })


@csrf_exempt
def start_payment_by_ids(request):
    if request.method == 'POST':
        payments_ids = json.loads(request.body)
        for id in payments_ids['ids']:
            payment_service.start_payment(id)
        return JsonResponse({
            "status": "ok",
            "data": None
        })
    return JsonResponse({
        "status": "err",
        "data": None
    })


@csrf_exempt
def get_balance(request):
    if request.method == 'GET':
        balance = balance_service.get_balance()
        return JsonResponse({
            "status": "ok",
            "data": balance
        })


@csrf_exempt
def clear_payment_list(request):
    if request.method == 'POST':
        payment_service.clear_payment_list()
        return HttpResponse("Ok")
    return HttpResponse("Err")
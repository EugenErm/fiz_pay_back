import json

from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from utils.validators.is_credit_card_validator import is_credit_card
from .dto.create_payment_dto import CreatePaymentDto
from .forms import UploadPaymentRegisterForm
from .services.balance_service import balance_service
from .services.payment_import_service import payment_import_service
from .services.payment_service import payment_service


@csrf_exempt
def upload_payment_list_file(request):
    if request.method == 'POST':
        form = UploadPaymentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                errors, result = payment_import_service.import_payments_from_file(form.files['file'])

                if len(errors) != 0:
                    return JsonResponse({
                        "status": "err",
                        "message": "Найдены ошибки в платежах",
                        "data": errors
                    })
                else:
                    return JsonResponse({
                        "status": "ok",
                        "data": list(map(lambda payment: model_to_dict(payment), result))
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
            "data": form.errors
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

import json

import pandas
from django.http import HttpResponse
from .forms import UploadPaymentRegisterForm
from django.views.decorators.csrf import csrf_exempt

from .services.payment_service import PaymentService

payment_service = PaymentService()


def handle_uploaded_payment_list(f) -> pandas.DataFrame:
    return pandas.read_csv(f, dtype="string").loc[:, ["name", "lastname", "middlename", "pam", "amount"]]


@csrf_exempt
def upload_payment_list_file(request):
    if request.method == 'POST':
        form = UploadPaymentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                payment_list = handle_uploaded_payment_list(form.files['file'])
                payment_service.import_payments_from_file(payment_list)

                return HttpResponse('Ok')

            except Exception as e:
                return HttpResponse(e)
        return HttpResponse(json.dumps({"err": form.errors}))
    return HttpResponse(json.dumps({"err": "is Not Post"}))


@csrf_exempt
def get_payment_list(request):
    payments = payment_service.get_payment_list()
    return HttpResponse(json.dumps(payments, default=str))
    # if request.GET:
    #     return HttpResponse("Hello")


@csrf_exempt
def start_payment_by_ids(request):
    if request.method == 'POST':
        payments_ids = json.loads(request.body)
        payment_service.start_payment_by_ids(payments_ids['ids'])
        return HttpResponse("Ok")
    return HttpResponse("Err")

@csrf_exempt
def clear_payment_list(request):
    if request.method == 'POST':
        payment_service.clear_payment_list()
        return HttpResponse("Ok")
    return HttpResponse("Err")

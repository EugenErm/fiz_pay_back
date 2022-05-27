import json
import os

import pandas
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadPaymentRegisterForm
from .services.payment_import_service import payment_import_service
from .services.payment_service import payment_service


@csrf_exempt
def upload_payment_list_file(request):
    if request.method == 'POST':
        form = UploadPaymentRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                payment_import_service.import_payments_from_file(form.files['file'])
                return HttpResponse('Ok')
            except Exception as e:
                return HttpResponse(e)
        return HttpResponse(json.dumps({"err": form.errors}))
    return HttpResponse(json.dumps({"err": "is Not Post"}))


@csrf_exempt
def get_payment_list(request):
    payments = payment_service.get_payment_list()
    return HttpResponse(json.dumps(payments, default=str))

@csrf_exempt
def get_payment_by_id(request, payment_id: int):
    payments = payment_service.get_payment_by_id(payment_id)
    return HttpResponse(serializers.serialize('json', [payments]))

@csrf_exempt
def start_payment_by_ids(request):
    if request.method == 'POST':
        payments_ids = json.loads(request.body)
        for id in payments_ids['ids']:
            payment_service.start_payment(id)
        return HttpResponse("Ok")
    return HttpResponse("Err")

@csrf_exempt
def clear_payment_list(request):
    if request.method == 'POST':
        payment_service.clear_payment_list()
        return HttpResponse("Ok")
    return HttpResponse("Err")

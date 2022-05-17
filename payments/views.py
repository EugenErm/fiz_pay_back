import json

import pandas
from django.http import HttpResponse, HttpResponseRedirect
from .forms import UploadPaymentRegisterForm
from django.views.decorators.csrf import csrf_exempt


def handle_uploaded_payment_list(f):
    return pandas.read_csv(f, dtype="string")


@csrf_exempt
def upload_file(request):
    print(request.FILES)
    form = UploadPaymentRegisterForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            form_data = handle_uploaded_payment_list(form.files['file'])
            print(form_data)
        except:
             return HttpResponse('Err')


    # print(form.files)
    # print(form.is_valid())
    #
    # print(pandas.read_csv(request.FILES['file'], dtype="string"))


    # if request.method == 'POST':
    #     form = UploadFileForm(request.POST, request.FILES)
    #     if form.is_valid():
    #         handle_uploaded_file(request.FILES['file'])
    #         return HttpResponseRedirect('/success/url/')
    # else:
    #     form = UploadFileForm()
    #
    # return json.dumps({"foo": "bar"})
    return HttpResponse('Ok')
from django import forms


class UploadPaymentRegisterForm(forms.Form):
    file = forms.FileField()

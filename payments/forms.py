from django import forms
import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv', '.xlsx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class UploadPaymentRegisterForm(forms.Form):
    file = forms.FileField(label="file", required=True, validators=[validate_file_extension])

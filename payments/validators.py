import re
from rest_framework.serializers import ValidationError
from utils.validators.is_credit_card_validator import is_credit_card


def is_credit_card_validator(text):
    if not is_credit_card(text):
        raise ValidationError(f"{text} is not credit card")

    return text

import pandas
from utils.validators.is_credit_card_validator import is_credit_card


def is_payment_valid(payment: pandas.Series) -> list:
    payment_na = payment.notna()
    errors = []
    if not payment_na.get('pam'):
        errors.append(f"pam is required")
    elif not is_credit_card(payment.get('pam')):
        errors.append(f"{payment['pam']} is not credit card")

    if not payment_na.get('name'):
        errors.append(f"name is required")

    if not payment_na.get('lastname'):
        errors.append(f"lastname is required")

    if not payment_na.get('amount'):
        errors.append(f"amount is required")
    else:
        try:
            int(payment['amount'])
        except:
            errors.append(f"amount err: {payment['amount']} is not int")

    return errors
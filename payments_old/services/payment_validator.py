import pandas
from utils.validators.is_credit_card_validator import is_credit_card


def is_payment_valid(payment: pandas.Series) -> list:
    payment_na = payment.notna()
    errors = []
    if not payment_na.get('pam'):
        errors.append(f"Не заполнено поле кредитня карта")
    elif not is_credit_card(payment.get('pam')):
        errors.append(f"{payment['pam']} кредитная карта не прошла валидацию")

    if not payment_na.get('name'):
        errors.append(f"Не заполнено поле имя")

    if not payment_na.get('lastname'):
        errors.append(f"Не заполнено поле фамилия")

    if not payment_na.get('amount'):
        errors.append(f"Не заполнено поле сумма")
    else:
        try:
            int(payment['amount'])
        except:
            errors.append(f"amount err: {payment['amount']} is not int")

    return errors
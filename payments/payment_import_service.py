import logging
import os
from typing import Optional

import pandas

from .exceptions import ImportCountLimitException
from .models import Payment
from .validators import is_credit_card_validator

_col_list = ["name", "lastname", "middlename", "pam", "amount"]
_payment_count_limit = 5000
_logger = logging.getLogger('app')


def import_payments_from_file(f, user) -> ([str], [Payment]):
    _logger.info(f"payment_import_service > import_payments_from_file -- start import file: {f.name}")
    pandas_payments = _read_pandas_payments_from_file(f)

    _validate_limits(pandas_payments)
    errors = _validate_payments(pandas_payments)

    if len(errors) != 0:
        return errors, []

    payments = _create_payments(pandas_payments, user)
    _logger.info(f"payment_import_service > import_payments_from_file -- end import file: {f.name}")
    return [], payments

def _create_payments(payments: pandas.DataFrame, user):
    created_payments = []
    for index, payment in payments.iterrows():
        payment = Payment(
            card_data=payment['pam'],
            amount=payment['amount'],
            name=payment['name'],
            last_name=payment['lastname'],
            middle_name=None if payment.isna()['middlename'] else payment['middlename'],
            user=user
        )
        payment.save()
        created_payments.append(payment)
    return created_payments


def _read_pandas_payments_from_file(f) -> pandas.DataFrame:
    ext = os.path.splitext(f.name)[1]
    csv_ext = ['.csv']
    xls_ext = ['.xlsx', '.xls']

    if ext.lower() in csv_ext:
        return pandas.read_csv(f, dtype="string").loc[:, _col_list]
    elif ext.lower() in xls_ext:
        return pandas.read_excel(f, dtype="string").loc[:, _col_list]


def _validate_payments(payments: pandas.DataFrame):
    file_errors = []
    for index, payment in payments.iterrows():
        errors = _is_payment_valid(payment)
        if not len(errors) == 0:
            file_errors.append((index, errors))
    return file_errors


def _is_payment_valid(payment: pandas.Series) -> list:
    payment_na = payment.notna()
    errors = []
    if not payment_na.get('pam'):
        errors.append(f"Не заполнено поле кредитня карта")
    else:
        try:
            is_credit_card_validator(payment.get('pam'))
        except Exception:
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

def _validate_limits(payments: pandas.DataFrame):
    if len(payments) >= _payment_count_limit:
        _logger.warning(f"payment_import_service > import_payments_from_file -- ImportCountLimitException: {len(payments)} <= {_payment_count_limit}")
        raise ImportCountLimitException(f'ImportCountLimitException {len(payments)} <= {_payment_count_limit}')





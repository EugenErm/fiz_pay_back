import os

import pandas

from payments.dto.create_payment_dto import CreatePaymentDto
from payments.services.payment_service import payment_service
from payments.services.payment_validator import is_payment_valid


class _PaymentImportService:
    col_list = ["name", "lastname", "middlename", "pam", "amount"]

    def __init__(self):
        self.payment_service = payment_service

    def import_payments_from_file(self, f):
        ext = os.path.splitext(f.name)[1]
        csv_ext = ['.csv']
        xls_ext = ['.xlsx', '.xls']

        if ext.lower() in csv_ext:
            self.import_payments_from_pandas_df(pandas.read_csv(f, dtype="string").loc[:, self.col_list])
        elif ext.lower() in xls_ext:
            self.import_payments_from_pandas_df(
                pandas.read_excel(f, dtype="string", sheet_name="payments").loc[:, self.col_list])

    def import_payments_from_pandas_df(self, payments: pandas.DataFrame):
        file_errors = self._validate_payments(payments)
        if not len(file_errors) == 0:
            raise Exception(file_errors)

        self._create(payments)

    def _validate_payments(self, payments: pandas.DataFrame):
        if len(payments) > 10000:
            raise Exception("Count > 10000")
        file_errors = []
        for index, payment in payments.iterrows():
            errors = is_payment_valid(payment)
            if not len(errors) == 0:
                file_errors.append((index, errors))
        return file_errors

    def _create(self, payments: pandas.DataFrame):
        for index, payment in payments.iterrows():
            self.payment_service.create_payment(CreatePaymentDto.parse_obj(
                {
                    "pam": payment['pam'],
                    "amount": payment['amount'],
                    "name": payment['name'],
                    "last_name": payment['lastname'],
                    "middle_name": None if payment.isna()['middlename'] else payment['middlename']
                }))


payment_import_service = _PaymentImportService()

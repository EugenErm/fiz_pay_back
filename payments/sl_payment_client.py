import logging
from xml.etree.ElementTree import Element, tostring

import requests_pkcs12
import xmltodict

from paymentcert.models import PaymentCert
from payments.exceptions import InvalidPaymentCertException, InvalidPaymentPointException
from payments.models import Payment

from django.conf import settings

from payments.types import ProviderPayment

logger = logging.getLogger('app')


class SLPaymentClient:
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    API_URL = settings.SL_API_URL

    def __init__(self, cert: PaymentCert):
        self.cert = cert
        self.service = settings.SL_SERVICE_OPEN
        self.logger = logger

    def create_provider_payment(self, payment: Payment) -> ProviderPayment:
        self.logger.debug(f"PaymentClient -- create_payout - Payment: {payment}")

        payment_request = Element('payment', {
            "id": str(payment.id),
            "sum": str(payment.amount),
            "check": "0",
            "service": self.service,
            "account": payment.card_data,
            "date": payment.created_at.strftime(self.DATE_FORMAT)
        })
        payment_request.append(Element('attribute', {'name': "full_name", 'value': _get_name(payment)}))
        payment_request.append(Element('attribute', {'name': "metadata", 'value': payment.metadata}))

        return _parse_payment_response(self._post(payment_request))

    def get_balance(self):
        self.logger.debug(f"PaymentClient -- get_balance")
        balance_request = Element('balance')
        return _parse_balance_response(self._post(balance_request))

    def get_payment_by_id(self, payment: Payment) -> ProviderPayment:
        self.logger.info(
            f"PaymentClient -- get_payout_by_id - Payment ID: {payment.id}; trans: {payment.operation_id}")
        get_payment_request = Element('status', {"id": str(payment.id)})
        return _parse_payment_response(self._post(get_payment_request))

    def _post(self, payment_request: Element):
        req_wrapper = Element('request', {'point': str(self.cert.point)})
        req_wrapper.append(payment_request)

        self.logger.info(f"PaymentClient -- _post - Request active cert: {self.cert}")
        self.logger.info(f"PaymentClient -- _post - Request body: {tostring(req_wrapper)}")

        try:
            result = requests_pkcs12.post(
                self.API_URL,
                data=tostring(req_wrapper),
                pkcs12_filename=self.cert.p12cert.path,
                pkcs12_password=self.cert.password
            )

            self.logger.info(f"PaymentClient -- _post - resp status: {result.status_code}")
            self.logger.info(f"PaymentClient -- _post - resp body: {result.text}")

            if result.status_code != 200:
                self.logger.error(f"PaymentClient -- _post - Request Error: {result.status_code}; {result.text}")
                raise Exception('PaymentClient not correct status')

            return result.text

        except Exception as e:
            self.logger.error(f"PaymentClient -- _post Error - Request : Request: {tostring(req_wrapper)}")
            self.logger.error(f"PaymentClient -- _post Error {e}")

            if str(e) == 'Invalid password or PKCS12 data':
                raise InvalidPaymentCertException('Invalid password or PKCS12 data') from None
            else:
                raise e


def _parce_response(response: str):
    try:
        result = xmltodict.parse(response)
        if result.get('error'):
            if result.get('error') == 'Certificate error! Wrong serial!':
                raise InvalidPaymentCertException('Certificate error! Wrong serial!')
            if result.get('error') == 'Point not found!':
                raise InvalidPaymentPointException('Point not found!') from None
            else:
                raise Exception(result.get('error'))

        return result
    except Exception as e:
        logger.error(f"PaymentClient -- parce_response - input: {response}, {e}")
        raise e from None


def _parse_payment_response(response: str) -> ProviderPayment:
    resp = _parce_response(response)

    try:
        result = resp['response']['result']

        provider_payment = ProviderPayment(
            id=result['@id'],
            state=result['@state'],
            substate=result['@substate'],
            code=result['@code'],
            final=result['@final'],
        )

        if result.get('@trans'):
            provider_payment.trans = result['@trans']

        if result.get('@server_time'):
            provider_payment.server_time = result['@server_time']

        if result.get('@process_time'):
            provider_payment.process_time = result['@process_time']

        if result.get('attribute'):
            attr_resp = result.get('attribute')
            if type(attr_resp) == list:
                for attr in attr_resp:
                    if attr.get('@name') == 'provider-error-text':
                        provider_payment.provider_error_text = attr['@value']
            else:
                if attr_resp.get('@name') == 'provider-error-text':
                    provider_payment.provider_error_text = attr_resp['@value']

        return provider_payment

    except Exception as e:
        logger.error(f"PaymentClient -- parse_payment_response -: {e}")
        raise e


def _parse_balance_response(response: str):
    resp = _parce_response(response)

    try:
        balance = {"amount": resp['response']['balance']['@balance']}
        return balance

    except Exception as e:
        logger.error(f"PaymentClient -- parse_balance_response -: {e}")
        raise e


def _get_name(payment: Payment) -> str:
    fio = f"{payment.last_name} {payment.name}"
    if payment.middle_name:
        fio += f" {payment.middle_name}"
    return fio
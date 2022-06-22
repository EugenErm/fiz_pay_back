import datetime
import logging
from os import path
from xml.etree.ElementTree import Element, tostring

import requests
import requests_pkcs12
import xmltodict

from paymentcert.models import PaymentCert
from payments.models import Payment


class _PaymentServiceSl:
    API_URL = "https://business.selfwork.ru/external/extended-cert"

    # API_URL = "https://testing.selfwork.ru/external/extended-cert"
    PRIVATE_KEY_PATH = path.join(path.dirname(__file__), 'point_274.crt.pem')
    CERT_PATH = path.join(path.dirname(__file__), "point_274.key.pem")
    SERVICE = '219'
    POINT = "274"

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    logger = logging.getLogger('app')

    def __init__(self):
        self.payment_cert_service = payment_cert_service

    def create_payout(self, payment_data: Payment):
        self.logger.debug(f"PaymentProviderSlAdapter -- create_payout - Payment: {payment_data}")

        payment = Element('payment', {
            "id": str(payment_data.id),
            "sum": str(payment_data.amount),
            "check": "0",
            "service": self.SERVICE,
            "account": payment_data.card_data,
            "date": self._format_date(payment_data.created_at)
        })
        payment.append(Element('attribute', {'name': "full_name", 'value': payment_data.fio}))
        payment.append(Element('attribute', {'name': "metadata", 'value': payment_data.metadata}))

        return self._status_to_resp_format(self._request(payment))

    def get_payout_by_id(self, payment: Payment):
        self.logger.debug(
            f"PaymentProviderSlAdapter -- get_payout_by_id - Payment ID: {payment.id}; trans: {payment.operation_id}")
        resp = self._request(Element('status', {"id": str(payment.id)}))
        return self._status_to_resp_format(resp)

    def get_balance(self) -> int:
        balance = self._request(Element('balance'))['response']['balance']['@balance']
        return int(balance)

    def _request(self, req_xml_element: Element):
        cert = self.payment_cert_service.get_last_cert()

        req = Element('request', {'point': str(cert.point)})
        req.append(req_xml_element)

        self.logger.debug(f"PaymentProviderSlAdapter -- _request - Request: {tostring(req)}")
        self.logger.debug(f"PaymentProviderSlAdapter -- _request - cert: {cert}")
        self.logger.debug(f"PaymentProviderSlAdapter -- _request - url: {self.API_URL}")

        res = requests_pkcs12.post(
            self.API_URL,
            data=tostring(req),
            pkcs12_filename=cert.p12cert.path,
            pkcs12_password=cert.password
        )

        self.logger.debug(f"PaymentProviderSlAdapter -- _request - Response status: {res}")
        self.logger.debug(f"PaymentProviderSlAdapter -- _request - Response: {res.text}")
        return xmltodict.parse(res.text)

    def _status_to_resp_format(self, resp):

        status = {
            "id": resp['response']['result']['@id'],
            "state": resp['response']['result']['@state'],
            "substate": resp['response']['result']['@substate'],
            "code": resp['response']['result']['@code'],
            "final": resp['response']['result']['@final'],
        }

        if resp['response']['result'].get('@trans'):
            status['trans'] = resp['response']['result']['@trans']

        if resp['response']['result'].get('@server_time'):
            status['server_time'] = resp['response']['result']['@server_time']

        if resp['response']['result'].get('@process_time'):
            status['process_time'] = resp['response']['result']['@process_time']

        if resp['response']['result'].get('attribute'):
            attr_resp = resp['response']['result'].get('attribute')
            if type(attr_resp) == list:
                for attr in attr_resp:
                    if attr.get('@name') == 'provider-error-text':
                        status['provider-error-text'] = attr['@value']
            else:
                if resp['response']['result']['attribute'].get('@name') == 'provider-error-text':
                    status['provider-error-text'] = resp['response']['result']['attribute']['@value']

        return status

    def _format_date(self, date: datetime.datetime):
        return date.strftime(self.DATE_FORMAT)


SERVICES = {
    'OPEN': '219'
}

logger = logging.getLogger('app')


def parce_response(response: str):
    try:
        result = xmltodict.parse(response)
        return result
    except Exception as e:
        logger.error(f"PaymentClient -- parce_response - input: {response}", e)


def parse_payment_response(response: str):
    resp = parce_response(response)

    try:
        status = {
            "id": resp['response']['result']['@id'],
            "state": resp['response']['result']['@state'],
            "substate": resp['response']['result']['@substate'],
            "code": resp['response']['result']['@code'],
            "final": resp['response']['result']['@final'],
        }

        if resp['response']['result'].get('@trans'):
            status['trans'] = resp['response']['result']['@trans']

        if resp['response']['result'].get('@server_time'):
            status['server_time'] = resp['response']['result']['@server_time']

        if resp['response']['result'].get('@process_time'):
            status['process_time'] = resp['response']['result']['@process_time']

        if resp['response']['result'].get('attribute'):
            attr_resp = resp['response']['result'].get('attribute')
            if type(attr_resp) == list:
                for attr in attr_resp:
                    if attr.get('@name') == 'provider-error-text':
                        status['provider-error-text'] = attr['@value']
            else:
                if resp['response']['result']['attribute'].get('@name') == 'provider-error-text':
                    status['provider-error-text'] = resp['response']['result']['attribute']['@value']

        return status

    except Exception as e:
        logger.error(f"PaymentClient -- parse_payment_response -: {e}")
        raise e


def parse_balance_response(response: str):
    resp = parce_response(response)

    try:
        balance = {"amount": resp['response']['balance']['@balance']}
        return balance

    except Exception as e:
        logger.error(f"PaymentClient -- parse_balance_response -: {e}")
        raise e


def get_name(payment: Payment) -> str:
    fio = f"{payment.last_name} {payment.name}"
    if payment.middle_name:
        fio += f" {payment.middle_name}"
    return fio


class PaymentClient:
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    API_URL = 'https://business.selfwork.ru/external/extended-cert'

    def __int__(self, payment: Payment, payment_cert: PaymentCert):
        self.payment_cert = payment_cert
        self.payment = payment
        self.service = SERVICES['OPEN']
        self.logger = logger

    def create_payment(self):
        self.logger.debug(f"PaymentClient -- create_payout - Payment: {self.payment}")

        payment_request = Element('payment', {
            "id": str(self.payment.id),
            "sum": str(self.payment.amount),
            "check": "0",
            "service": self.service,
            "account": self.payment.card_data,
            "date": self.payment.created_at.strftime(self.DATE_FORMAT)
        })
        payment_request.append(Element('attribute', {'name': "full_name", 'value': get_name(self.payment)}))
        payment_request.append(Element('attribute', {'name': "metadata", 'value': self.payment.metadata}))

        return parse_payment_response(self._post(payment_request))

    def get_balance(self):
        self.logger.debug(f"PaymentClient -- get_balance")
        balance_request = Element('balance')
        return parse_balance_response(self._post(balance_request))

    def get_payment_by_id(self):
        self.logger.debug(
            f"PaymentClient -- get_payout_by_id - Payment ID: {self.payment.id}; trans: {self.payment.operation_id}")
        get_payment_request = Element('status', {"id": str(self.payment.id)})

        return parse_payment_response(self._post(get_payment_request))

    def _post(self, payment_request: Element):
        req_wrapper = Element('request', {'point': str(self.payment_cert.point)})
        req_wrapper.append(payment_request)

        self.logger.debug(f"PaymentClient -- _post - Request: {tostring(req_wrapper)}")

        try:
            result = requests_pkcs12.post(
                self.API_URL,
                data=tostring(req_wrapper),
                pkcs12_filename=self.payment_cert.p12cert.path,
                pkcs12_password=self.payment_cert.password
            )

            if result.status_code != 200:
                self.logger.error(f"PaymentClient -- _post - Request Error: {result.status_code}; {result.text}")
                raise Exception('PaymentClient not correct status')

            return result.text

        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f"PaymentClient -- _post Error - Request : Request: {tostring(req_wrapper)}")

            raise Exception('Request Error')

    def _get_active_cert(self, payment: Payment):
        user_id = payment.user_id
        return self.payment_cert.objects.filter(user_id=user_id).last()

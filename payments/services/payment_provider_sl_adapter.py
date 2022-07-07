import datetime
import logging
from os import path
from xml.etree.ElementTree import Element, tostring

import requests
import requests_pkcs12
import xmltodict

from payments.models import Payment


# Новый сертификат сгенерирован, не забудьте сохранить изменения. 274 Пароль: noWY94QwVv
from payments.services.payment_cert_service import payment_cert_service


class _PaymentProviderSlAdapter:
    # API_URL = "https://business.selfwork.ru/external/extended-cert"
    # API_URL = "https://testing.selfwork.ru/external/extended-cert"

    # PRIVATE_KEY_PATH = path.join(path.dirname(__file__), 'point_274.crt.pem')
    # CERT_PATH = path.join(path.dirname(__file__), "point_274.key.pem")

    API_URL = "https://business.selfwork.ru/external/extended-cert"
    # P12_CRT_PATH = path.join(path.dirname(__file__), 'point_588.p12')
    # P12_PASS = "t4K3o3QDrg"
    # SERVICE = '219'
    # POINT = "588"

    # API_URL = "https://testing.selfwork.ru/external/extended-cert"
    PRIVATE_KEY_PATH = path.join(path.dirname(__file__), 'point_274.crt.pem')
    CERT_PATH = path.join(path.dirname(__file__), "point_274.key.pem")
    SERVICE = '228'
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

    def get_payout_by_id(self, id: int):
        self.logger.debug(f"PaymentProviderSlAdapter -- get_payout_by_id - Payment ID: {id}")
        resp = self._request(Element('status', {"id": str(id)}))
        return self._status_to_resp_format(resp)

    def get_balance(self) -> int:
        balance = self._request(Element('balance'))['response']['balance']['@balance']
        return int(balance)

    def _request(self, req_xml_element: Element):
        cert = self.payment_cert_service.get_last_cert()

        req = Element('request', {'point': str(cert.point)})
        req.append(req_xml_element)

        self.logger.debug(f"PaymentProviderSlAdapter -- _request - Request: {tostring(req)}")

        # res = requests.post(self.API_URL, data=tostring(req), cert=(self.PRIVATE_KEY_PATH, self.CERT_PATH,))


        print(path.join(path.dirname(__file__), 'point_588.p12'))
        print(cert.p12cert.path)


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





payment_provider_adapter = _PaymentProviderSlAdapter()

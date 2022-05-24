import datetime
from os import path
from xml.etree.ElementTree import Element, tostring

import requests
import xmltodict

from payments.models import Payment


# Новый сертификат сгенерирован, не забудьте сохранить изменения. 274 Пароль: noWY94QwVv


class _PaymentProviderSlAdapter:
    # API_URL = "https://business.selfwork.ru/external/extended-cert"
    API_URL = "https://testing.selfwork.ru/external/extended-cert"

    PRIVATE_KEY_PATH = path.join(path.dirname(__file__), 'point_274.crt.pem')
    CERT_PATH = path.join(path.dirname(__file__), "point_274.key.pem")

    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, point):
        self.POINT = point
        self.SERVICE = '189'

    def create_payout(self, payment_data: Payment):
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

    def get_payout_by_id(self, id):
        resp = self._request(Element('status', {"id": str(id)}))
        return self._status_to_resp_format(resp)

    def get_balance(self) -> int:
        balance = self._request(Element('balance'))['response']['balance']['@balance']
        return int(balance)

    def _request(self, req_xml_element: Element):
        req = Element('request', {'point': str(self.POINT)})
        req.append(req_xml_element)

        print(tostring(req))

        res = requests.post(self.API_URL, data=tostring(req), cert=(self.PRIVATE_KEY_PATH, self.CERT_PATH,))
        print(res.text)
        return xmltodict.parse(res.text)

    def _status_to_resp_format(self, resp):

        status = {
            "id": resp['response']['result']['@id'],
            "state": resp['response']['result']['@state'],
            "substate": resp['response']['result']['@substate'],
            "code": resp['response']['result']['@code'],
            "final": resp['response']['result']['@final'],
            "trans": resp['response']['result']['@trans'],
            "server_time": resp['response']['result']['@server_time'],
        }

        if resp['response']['result'].get('@process_time'):
            status['process_time'] = resp['response']['result']['@process_time']

        if resp['response']['result'].get('attribute'):
            if resp['response']['result']['attribute'].get('@name') == 'provider-error-text':
                status['provider-error-text'] = resp['response']['result']['attribute']['@value']

        return status

    def _format_date(self, date: datetime.datetime):
        return date.strftime(self.DATE_FORMAT)


payment_provider_adapter = _PaymentProviderSlAdapter(point='274')

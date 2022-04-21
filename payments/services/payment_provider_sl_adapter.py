from os import path
from xml.etree.ElementTree import Element, tostring
import xmltodict
import requests

from payments.models import Payment


# Новый сертификат сгенерирован, не забудьте сохранить изменения. 274 Пароль: noWY94QwVv




class PaymentProviderSlAdapter:
    # API_URL = "https://business.selfwork.ru/external/extended-cert"
    API_URL = "https://testing.selfwork.ru/external/extended-cert"

    PRIVATE_KEY_PATH = path.join(path.dirname(__file__), 'point_274.crt.pem')
    CERT_PATH = path.join(path.dirname(__file__), "point_274.key.pem")

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
            "date": payment_data.created_at.isoformat()
        })
        payment.append(Element('attribute', {'name': "full_name", 'value': payment_data.fio}))
        payment.append(Element('attribute', {'name': "metadata", 'value': payment_data.metadata}))

        print(self._request(payment))
        pass

    def get_payout_by_id(self, id):
        print(self._request(Element('status', {"id": id})))

    def get_balance(self) -> int:
        balance = self._request(Element('balance'))['response']['balance']['@balance']
        return int(balance)


    def _request(self, req_xml_element: Element):
        req = Element('request', {'point': str(self.POINT)})
        req.append(req_xml_element)

        print(tostring(req))

        res = requests.post(self.API_URL, data=tostring(req), cert=(self.PRIVATE_KEY_PATH, self.CERT_PATH,))
        return xmltodict.parse(res.text)

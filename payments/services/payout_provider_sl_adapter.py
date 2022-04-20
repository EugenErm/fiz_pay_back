from xml.etree.ElementTree import Element

import requests

from payments.models import Payment




class PayoutProviderSlAdapter:
    API_URL = "https://business.selfwork.ru/external/extended-cert"

    def __init__(self):
        self.POINT = ''
        self.CERT = ''
        self.SERVICE = ''

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
        print(self._request(Element('balance')))

        return 1

    def _request(self, req_xml_element: Element):
        req = Element('request', {'point': str(self.POINT)})
        req.append(req_xml_element)

        res = requests.post(self.API_URL, data=req, cert=(self.PRIVATE_KEY_PATH, self.CERT_PATH,))

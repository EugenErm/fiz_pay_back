
from paymentcert.models import PaymentCert



class _PaymentCertService:

    def __init__(self):
        self.payment_cert_model = PaymentCert

    def load_cert(self, point, name, password, cert_file):
        payment_cert = self.payment_cert_model(
            point=point,
            name=name,
            password=password,
            p12cert=cert_file
        )
        payment_cert.save()

    def get_last_cert(self) -> PaymentCert:
        return self.payment_cert_model.objects.last()


payment_cert_service = _PaymentCertService()

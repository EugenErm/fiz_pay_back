from payments.sl_payment_client import SLPaymentClient
from .models import PaymentCert



def get_active_cert(user_id: int) -> PaymentCert:
    return PaymentCert.objects.filter(user_id=user_id).last()

def check_cert(paymentCert: PaymentCert):
    client = SLPaymentClient(cert=paymentCert)
    return client.check_cert()


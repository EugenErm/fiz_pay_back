from paymentcert.models import PaymentCert
from paymentcert.services import get_active_cert
from payments.models import Payment


from .sl_payment_service import SLPaymentClient

def start_provider_payment(payment_id: int):
    payment = Payment.objects.get(pk=payment_id)
    print(payment)
    cert = get_active_cert(user_id=payment.user_id)
    client = SLPaymentClient(cert=cert)

    return client.create_provider_payment(payment)





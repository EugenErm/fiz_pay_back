from paymentcert.models import PaymentCert
from payments.models import Payment
from payments.payment_service_sl import PaymentClient


def _get_payment_client(payment_id: int)-> PaymentClient:
    payment = Payment.objects.get(pk=payment_id)
    payment_cert = PaymentCert.objects.filter(user_id=payment.user_id).last()
    return PaymentClient(payment,payment_cert)

def start_provider_payment(payment_id: int):
    payment_client = _get_payment_client(payment_id)
    logger.debug(f"Thread '{threading.current_thread().name}' -- Start provider payment ID: {payment.id}")
    return payment_client.create_payout(payment)
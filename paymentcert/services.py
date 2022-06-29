from .models import PaymentCert


def get_active_cert(user_id: int) -> PaymentCert:
    return PaymentCert.objects.filter(user_id=user_id).last()

from payments.models import Payment
from payments.services.payment_provider_sl_adapter import PaymentProviderSlAdapter


class PaymentService:
    provider = PaymentProviderSlAdapter(point='274')

    def get_balance(self):
        print(self.provider.get_balance())

    def create_payment(self):
        payment = Payment(fio='Test Test Tes', card_data='4000000000000002', amount=1000)
        # print(payment.id)
        payment.save()
        print(payment.id)


    def get_payment_info(self, id):
        pass

import logging

from payments.services.payment_provider_sl_adapter import payment_provider_adapter


class _BalanceService:

    def __init__(self):
        self.payment_provider_adapter = payment_provider_adapter
        self.logger = logging.getLogger('app')

    def get_balance(self):
        return self.payment_provider_adapter.get_balance()


balance_service = _BalanceService()

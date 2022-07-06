class IncorrectPaymentStatusException(Exception):
    pass


class InvalidPaymentCertException(Exception):
    pass


class InvalidPaymentPointException(Exception):
    pass


class ProviderPaymentNotFoundException(Exception):
    pass


class ImportCountLimitException(Exception):
    pass

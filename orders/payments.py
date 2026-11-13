class PaymentHandler:
    """Base class for payment methods."""

    code = ''

    def initiate(self, order):
        """
        Start payment for a freshly created order.

        Return a URL to send the customer to (for example a hosted payment
        page), or ``None`` when no redirect is needed.
        """
        raise NotImplementedError


class CashOnDeliveryHandler(PaymentHandler):
    code = 'cod'

    def initiate(self, order):
        # Nothing is charged online. Payment stays "pending" until the order
        # is delivered and the rider collects the cash.
        return None


PAYMENT_HANDLERS = {
    CashOnDeliveryHandler.code: CashOnDeliveryHandler(),
}


def get_payment_handler(method):
    try:
        return PAYMENT_HANDLERS[method]
    except KeyError:
        raise ValueError(f'Unsupported payment method: {method}')

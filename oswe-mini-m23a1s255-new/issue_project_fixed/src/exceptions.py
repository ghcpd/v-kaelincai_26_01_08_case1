"""Custom exceptions for shipping service."""


class NoValidShippingMethodFoundException(Exception):
    """Raised when no valid shipping method is available for the order."""

    def __init__(self, message="No valid shipping method found for this order"):
        self.message = message
        super().__init__(self.message)


class InvalidOrderException(Exception):
    """Raised when order data is invalid."""
    pass

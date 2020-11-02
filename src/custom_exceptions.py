
class SameTransactionException(Exception):
    """
    Raise in case of transaction lives in cache database
    """
    pass


class NoStockError(Exception):
    """
    Raise in case user wants to sell stock without owning it
    """
    pass


class NotEnoughBalanceError(Exception):
    """
    Raise in case user does not have enough balance
    """
    pass


class InvalidOperationError(Exception):
    """
    Raise if operation is not valid
    """
    pass


class InvalidDataError(Exception):
    """
    Raise if data cannot be casted to Decimal
    """
    pass


class ServiceNotAvailable(Exception):
    """
    Raise if service is out of service
    """
    pass


class NegativeValuesError(Exception):
    """
    Raise if values are negatives
    """
    pass


class TimestampError(Exception):
    """
    Raise if timestamp has a problem
    """
    pass

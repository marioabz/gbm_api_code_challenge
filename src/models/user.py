from decimal import Decimal
from dataclasses import dataclass


@dataclass
class User:

    id: int
    issuers: list
    cash: Decimal

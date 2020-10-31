from decimal import Decimal
from dataclasses import dataclass


@dataclass
class User:

    id: str
    issuers: list
    cash: Decimal

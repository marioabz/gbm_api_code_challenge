from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class Transaction:

    id: int
    time: str
    shares: int
    operation: str
    price: Decimal
    change: Decimal
    issuer_name: str
    user_balance: Decimal

    # Composite Primary Key
    pk: str = field(
        init=False,
        metadata={
            'name': 'Partition Key',
            'type': 'hash',
            'hashed': False,
            'structure': 'transaction#{id}'
        }
    )

    # Sort key
    sk: str = field(
        init=False,
        metadata={
            'name': 'Partition Key',
            'type': 'hash',
            'hashed': False,
            'structure': "issuer#{time}#{issuer_name}"
        }
    )

    def __post_init__(self):
        """Creates Partition and Sort keys checks data integrity against entity constraints."""

        # Composite Primary key creation
        setattr(self, 'pk', f"transaction#{self.id}#{self.operation}")
        setattr(self, 'sk', f"issuer#{self.time}#{self.issuer_name}")

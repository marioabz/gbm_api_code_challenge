from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class Transaction:
    """
    The transaction class allows the developer to encapsulate
    the needed data to store a transaction enforcing the data
    types and adding the cash balance along with the shares balance
    to every transaction so that cash balance is trackable from
    transaction number zero.
    'Pk', meaning 'primary key', and 'sk' meaning 'sort key' are
    the queryable properties of the model
    """

    id: int
    time: str
    operation: str
    issuer_name: str
    share_price: Decimal
    user_shares: Decimal
    change_cash: Decimal
    total_shares: Decimal
    user_balance: Decimal
    change_shares: Decimal

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
        setattr(self, 'pk', f"transaction#{self.id}")
        setattr(self, 'sk', f"issuer#{self.time}#{self.issuer_name}")

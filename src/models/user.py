from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class User:

    id: int
    issuers: list
    cash: Decimal

    pk: str = field(
        init=False,
        metadata={
            'name': 'Partition Key',
            'type': 'hash',
            'hashed': False,
            'structure': '{id}'
        }
    )

    def __post_init__(self):
        """Creates Partition and Sort keys checks data integrity against entity constraints."""

        # Composite Primary key creation
        setattr(self, 'pk', f"user#{self.id}")

from decimal import Decimal
from dataclasses import dataclass, field


@dataclass
class User:

    id: str
    cash: Decimal

    pk: str = field(
        init=False,
        metadata={
            'name': 'Partition Key',
            'type': 'hash',
            'hashed': False,
            'structure': 'user#{id}'
        }
    )

    sk: str = field(
        init=False,
        metadata={
            'name': 'Sort Key',
            'type': 'hash',
            'hashed': False,
            'structure': '{id}'
        }
    )

    def __post_init__(self):
        """Creates Partition and Sort keys checks data integrity against entity constraints."""

        # Composite Primary key creation
        setattr(self, 'pk', f"user")
        setattr(self, 'sk', f"{self.id}".zfill(10))

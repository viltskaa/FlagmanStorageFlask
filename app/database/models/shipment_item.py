from dataclasses import dataclass
from datetime import datetime
@dataclass
class ShipmentItem:
    id: int
    article: str
    count_cur: int
    count_all: int
    worker_id: int = 0
    created_at: datetime = None
    is_active: bool = False

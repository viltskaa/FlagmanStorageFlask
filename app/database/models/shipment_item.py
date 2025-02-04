from dataclasses import dataclass
from datetime import date, time
@dataclass
class ShipmentItem:
    id: int
    article: str
    count_cur: int
    count_all: int
    worker_id: int = 0
    created_date: date = None
    created_time: time = None
    is_active: str = "RECEIVED"

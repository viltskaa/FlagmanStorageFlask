from dataclasses import dataclass
from datetime import date, time, datetime


@dataclass
class ShipmentItem:
    id: int
    order_id: int
    article: str
    orderUid: str
    for_this: str
    scanned: str
    scanned_time: datetime
    worker_id: int = 0
    created_date: date = None
    created_time: time = None
    action_time: time = None
    is_active: str = "RECEIVED"


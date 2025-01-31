from dataclasses import dataclass
from datetime import datetime


@dataclass
class OnShipment:
    id: int
    shipment_id: int
    qrcode: str

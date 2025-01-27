from dataclasses import dataclass


@dataclass
class Item:
    id: int
    article: str
    qrcode: str
    worker_id: int = 0
    status: str = "STORAGE"

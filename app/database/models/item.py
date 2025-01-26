from dataclasses import dataclass


@dataclass
class Item:
    id: int
    article: str
    qrcode: str
    status: str = "STORAGE"

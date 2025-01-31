from typing import Optional
from app.repositories import OnShipmentRepository

class OnShipmentService:
    @staticmethod
    def insert(shipment_id: int, qrcode: str) -> Optional[int]:
        return OnShipmentRepository.insert(shipment_id, qrcode)

    @staticmethod
    def check_qrcode_not_exists(qrcode:str) -> bool:
        return OnShipmentRepository.check_qrcode_not_exists(qrcode)

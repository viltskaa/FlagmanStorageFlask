from typing import Optional
from app.repositories import OnShipmentRepository

class OnShipmentService:
    @staticmethod
    def insert(shipment_id: int, qrcode: str) -> Optional[int]:
        return OnShipmentRepository.insert(shipment_id, qrcode)

    @staticmethod
    def check_qrcode_not_exists(qrcode: str) -> bool:
        return OnShipmentRepository.check_qrcode_not_exists(qrcode)

    @staticmethod
    def remove_if_ids(ids: list[int]) -> bool:
        return OnShipmentRepository.remove_if_ids(ids)

    @staticmethod
    def get_qrcodes(ids: list[int]) -> list[str]:
        return OnShipmentRepository.get_qrCodes(ids)

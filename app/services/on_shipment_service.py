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
    def get_count_by_shipment_id(shipment_id: int) -> Optional[int]:
        return OnShipmentRepository.get_count_by_shipment_id(shipment_id)

    @staticmethod
    def get_qrcodes(ids: list[int]) -> list[str]:
        return OnShipmentRepository.get_qrCodes(ids)

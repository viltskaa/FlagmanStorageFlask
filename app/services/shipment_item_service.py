from datetime import datetime, timedelta
from typing import Optional
from app.database import ShipmentItem
from flask import current_app
from .on_shipment_service import OnShipmentService
from .item_service import ItemService
from .worker_service import WorkerService
from app.repositories import ShipmentItemRepository


class ShipmentItemService:
    @staticmethod
    def insert(article: str, order_id: str, date: datetime, status: str, for_this: str) -> Optional[int]:
        return ShipmentItemRepository.insert(article, order_id, date, status, for_this)

    @staticmethod
    def get_all(worker_id: int) -> list[dict]:
        tokens = WorkerService.get_tokens(worker_id)
        return ShipmentItemRepository.get_all(tokens)

    @staticmethod
    def get_all_by_period(date_start: datetime, date_end: datetime, status: str) -> list[ShipmentItem]:
        return ShipmentItemRepository.get_all_by_period(date_start, date_end, status)
    @staticmethod
    def check_all_count_cur_equals_count_all(user_id: int) -> bool:
        tokens = WorkerService.get_tokens(user_id)
        return ShipmentItemRepository.check_all_count_cur_equals_count_all(tokens)

    @staticmethod
    def process_qr_scan(qrcode: str, article: str, user_id: int) -> bool:
        try:
            if not ItemService.check_with_status(qrcode):
                return False

            if not OnShipmentService.check_qrcode_not_exists(qrcode):
                return False
            tokens = WorkerService.get_tokens(user_id)
            shipment_item = ShipmentItemRepository.get_active_shipment_by_article(article, tokens)
            if not shipment_item:
                return False

            shipment_id = shipment_item.id

            if not OnShipmentService.insert(shipment_id, qrcode):
                return False

            ShipmentItemRepository.update_scanned(shipment_id, user_id)

            return True

        except Exception as e:
            current_app.logger.error(f"Ошибка в process_qr_scan: {e}")
            return False

    @staticmethod
    def handle_out_of_stock(item_id: int,worker_id: int) -> tuple[bool, str]:
        shipment = ShipmentItemRepository.get_by_id(item_id)
        if shipment is None:
            return False, "Item not found"

        tomorrow = datetime.now() + timedelta(days=1)
        if shipment.is_active == 'POSTPONED':
            return False, "Item has already been rescheduled 1 time"
        print(shipment.id)
        if not ShipmentItemRepository.insert(shipment.article, shipment.count_all - shipment.count_cur, tomorrow,
                                             'POSTPONED', shipment.for_this,worker_id):
            return False, "Failed to insert new Item in the database"

        if shipment.count_cur == 0:
            if not ShipmentItemRepository.delete(item_id):
                return False, "Failed to delete Item in the database"
        else:
            if not ShipmentItemRepository.update_count_all(item_id, shipment.count_cur,worker_id):
                return False, "Failed to update Item in the database"

        return True, "Success"
    @staticmethod
    def shipment_all(user_id:int) -> bool:
        try:
            if not ShipmentItemRepository.update_today(user_id):
                return False
            shipment_ids = ShipmentItemRepository.get_all_true()
            if not shipment_ids:
                return False
            qr_codes = OnShipmentService.get_qrcodes(shipment_ids)
            if not qr_codes:
                return False
            if not ItemService.shipment(qr_codes, user_id):
                return False
            return True
        except Exception as e:
            current_app.logger.error(f"Ошибка в shipment_all: {e}")
            return False

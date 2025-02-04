from datetime import datetime, timedelta
from typing import Optional
import requests
from app.database import ShipmentItem
import logging
from flask import current_app
from .on_shipment_service import OnShipmentService
from .item_service import ItemService
from app.repositories import ShipmentItemRepository


class ShipmentItemService:
    @staticmethod
    def insert(article: str, count_all: int, date: datetime, status: str) -> Optional[int]:
        return ShipmentItemRepository.insert(article, count_all, date, status)

    @staticmethod
    def get_all() -> list[ShipmentItem]:
        return ShipmentItemRepository.get_all()

    @staticmethod
    def check_all_count_cur_equals_count_all() -> bool:
        return ShipmentItemRepository.check_all_count_cur_equals_count_all()

    @staticmethod
    def process_qr_scan(qrcode: str, article: str) -> bool:
        try:
            if not ItemService.check_with_status(qrcode):
                return False

            if not OnShipmentService.check_qrcode_not_exists(qrcode):
                return False

            shipment_item = ShipmentItemRepository.get_active_shipment_by_article(article)
            if not shipment_item:
                return False

            shipment_id = shipment_item.id

            current_count = OnShipmentService.get_count_by_shipment_id(shipment_id)

            if current_count >= shipment_item.count_all:
                return False

            if not OnShipmentService.insert(shipment_id, qrcode):
                return False

            ShipmentItemRepository.update_count_cur(shipment_id, current_count + 1)

            return True

        except Exception as e:
            current_app.logger.error(f"Ошибка в process_qr_scan: {e}")
            return False

    @staticmethod
    def handle_out_of_stock(item_id: int) -> tuple[bool, str]:
        shipment = ShipmentItemRepository.get_by_id(item_id)
        if shipment is None:
            return False, "Item not found"

        tomorrow = datetime.now() + timedelta(days=1)
        if shipment.is_active == 'POSTPONED':
            return False, "Item has already been rescheduled 1 time"

        if not ShipmentItemRepository.insert(shipment.article, shipment.count_all - shipment.count_cur, tomorrow, 'POSTPONED'):
            return False, "Failed to insert new Item in the database"

        if shipment.count_cur == 0:
            if not ShipmentItemRepository.delete(item_id):
                return False, "Failed to delete Item in the database"
        else:
            if not ShipmentItemRepository.update_count_all(item_id, shipment.count_cur):
                return False, "Failed to update Item in the database"

        return True, "Success"
    @staticmethod
    def shipment_all() -> bool:
        try:
            if not ShipmentItemRepository.update_today():
                return False
            shipment_ids = ShipmentItemRepository.get_all_true()
            if not shipment_ids:
                return False
            print(shipment_ids)
            qr_codes = OnShipmentService.get_qrcodes(shipment_ids)
            if not qr_codes:
                print("тута?")
                return False
            if not ItemService.shipment(qr_codes):
                return False
            return True
        except Exception as e:
            current_app.logger.error(f"Ошибка в shipment_all: {e}")
            return False

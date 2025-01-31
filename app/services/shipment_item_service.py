from datetime import datetime
from typing import Optional
import requests
from app.database import ShipmentItem
import logging
from flask import current_app
from app.services import ItemService, OnShipmentService
from app.repositories import ShipmentItemRepository


class ShipmentItemService:
    @staticmethod
    def insert(article: str, count_all: int, date: datetime) -> Optional[int]:
        return ShipmentItemRepository.insert(article, count_all, date)

    @staticmethod
    def get_all() -> list[ShipmentItem]:
        return ShipmentItemRepository.get_all()

    @staticmethod
    def check_all_count_cur_equals_count_all() -> bool:
        return ShipmentItemRepository.check_all_count_cur_equals_count_all()

    @staticmethod
    def process_qr_scan(qrcode: str, article: str) -> bool:
        try:
            if not ItemService.check_with_status(qrcode): # Проверка, что qr есть в item
                return False

            if not OnShipmentService.check_qrcode_not_exists(qrcode): # Проверка, что qr нет в onShipment
                return False

            shipment_item = ShipmentItemRepository.get_active_shipment_by_article(article)
            if not shipment_item:
                return False

            shipment_id = shipment_item.id

            new_count_cur = shipment_item.count_cur + 1
            if new_count_cur > shipment_item.count_all:
                return False

            ShipmentItemRepository.update_count_cur(shipment_id, new_count_cur) # Обновление тек. отсканированого в shipmentItem

            OnShipmentService.insert(shipment_id, qrcode) # добавление в onShipment

            return True

        except Exception as e:
            current_app.logger.error(f"Ошибка в process_qr_scan: {e}")
            return False

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
    def check_all_fully_scanned(user_id: int) -> bool:
        tokens = WorkerService.get_tokens(user_id)
        return ShipmentItemRepository.is_order_fully_scanned(tokens)

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
            print("я тут был")
            shipment_id = shipment_item.id

            if not OnShipmentService.insert(shipment_id, qrcode):
                return False

            ShipmentItemRepository.update_scanned(shipment_id, user_id)

            return True

        except Exception as e:
            current_app.logger.error(f"Ошибка в process_qr_scan: {e}")
            return False

    @staticmethod
    def handle_out_of_stock(orderUid: str,full_name: str) -> tuple[bool, str]:
        user = WorkerService.get_worker(full_name)
        if not user:
            return False,"Такого пользователя нет"
        if user.get('role') != 'BRIGADIER':
            return False, "Роль пользователя не бригадир"
        worker_id = user.get('id')
        if not ShipmentItemRepository.stock(orderUid,worker_id):
            return False, "Не удалось осуществить перенос"
        shipment_ids = ShipmentItemRepository.get_by_orderUid(orderUid)
        if not shipment_ids:
            return False, "Не удалось осуществить перенос"
        if not OnShipmentService.remove_if_ids(shipment_ids):
            return False, "Не удалось осуществить перенос"
        return True, "Перенос успешен"
    @staticmethod
    def shipment_all(user_id:int) -> bool:
        try:
            if not ShipmentItemRepository.update_status_of_fully_scanned_items(user_id):
                return False
            shipment_ids = ShipmentItemRepository.get_all_true(user_id)
            if not shipment_ids:
                return False
            qr_codes = OnShipmentService.get_qrcodes(shipment_ids)
            if not qr_codes:
                return False
            if not ItemService.shipment(qr_codes, user_id):
                return False
            not_shipment_ids = ShipmentItemRepository.get_ids_of_partially_scanned_items(user_id)
            print(not_shipment_ids)
            if not_shipment_ids:
                if not OnShipmentService.remove_if_ids(not_shipment_ids):
                    return False
                if not ShipmentItemRepository.update_status_of_ids(not_shipment_ids):
                    return False
            return True
        except Exception as e:
            current_app.logger.error(f"Ошибка в shipment_all: {e}")
            return False

    @staticmethod
    def cancel(orderUid: str) -> bool:
        try:
            if not ShipmentItemRepository.update_not_scanned(orderUid):
                return False
            shipment_ids = ShipmentItemRepository.get_by_orderUid(orderUid)
            print(shipment_ids)
            if not shipment_ids:
                return False
            if not OnShipmentService.remove_if_ids(shipment_ids):
                return False
            return True
        except Exception as e:
            current_app.logger.error(f"Ошибка в cancel: {e}")
            return False


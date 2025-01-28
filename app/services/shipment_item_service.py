from datetime import datetime
from typing import Optional
import requests
from app.database import ShipmentItem
import logging
from app.repositories import ShipmentItemRepository


class ShipmentItemService:
    @staticmethod
    def insert(article: str, count_all: int, date:datetime) -> Optional[int]:
        return ShipmentItemRepository.insert(article,count_all,date)

    @staticmethod
    def get_all() -> list[ShipmentItem]:
        return ShipmentItemRepository.get_all()

    @staticmethod
    def get_by_article(article: str) -> Optional[ShipmentItem]:
        return ShipmentItemRepository.get_by_article(article)

    @staticmethod
    def get_by_id(id: int) -> Optional[ShipmentItem]:
        return ShipmentItemRepository.get_by_id(id)

    @staticmethod
    def delete_by_id(id: int):
        return ShipmentItemRepository.delete(id)

    @staticmethod
    def update_count_cur(id: int, count_cur: int) -> bool:
        return ShipmentItemRepository.update_count_cur(id, count_cur)

    @staticmethod
    def update_count_all(id: int, count_cur: int) -> bool:
        return ShipmentItemRepository.update_count_all(id, count_cur)

    @staticmethod
    def check_all_count_cur_equals_count_all() -> bool:
        return ShipmentItemRepository.check_all_count_cur_equals_count_all()

    @staticmethod
    def update_today_is_active() -> bool:
        return ShipmentItemRepository.update_all_today()
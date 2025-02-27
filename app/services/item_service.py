from datetime import datetime
from typing import Optional
import requests
from app.database import Item
import logging
from app.repositories import ItemRepository

class ItemService:
    @staticmethod
    def get_all() -> list[Item]:
        return ItemRepository.get_all()

    @staticmethod
    def get_all_by_period(date_start: datetime,date_end: datetime, status:str) -> list[Item]:
        return ItemRepository.get_all_by_period(date_start,date_end,status)

    @staticmethod
    def insert(article: str, qrcode: str,user_id: int) -> Optional[int]:
        return ItemRepository.insert(article, qrcode,user_id)

    @staticmethod
    def write_off(qrcode: str,user_id: int) -> Optional[int]:
        return ItemRepository.write_off(qrcode, user_id)

    @staticmethod
    def shipment(qrcodes: list[str], worker_id: int) -> bool:
        return ItemRepository.shipment(qrcodes,worker_id)

    @staticmethod
    def get_by_article(article: str) -> Item:
        return ItemRepository.get_by_article(article)

    @staticmethod
    def delete_by_id(item_id: int) -> None:
        ItemRepository.delete_by_id(item_id)

    @staticmethod
    def delete_all() -> None:
        ItemRepository.delete_all()

    @staticmethod
    def check(qrcode: str) -> bool:
        return ItemRepository.check_if_exists(qrcode)

    @staticmethod
    def check_with_status(qrcode: str) -> bool:
        return ItemRepository.check_if_exists_and_status(qrcode)

    @staticmethod
    def check_with_status_write_off(qrcode: str) -> bool:
        return ItemRepository.check_if_exists_and_status_write_off(qrcode)


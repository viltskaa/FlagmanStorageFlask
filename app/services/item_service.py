from typing import Optional
import requests
from app.database import Item
import logging
from app.repositories import ItemRepository

WILDBERRIES_API_KEY = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTczMDQxNjI3NiwiaWQiOiI0NGJhZDg4Zi01ZjEwLTQ5MGYtODk4MS05ZjRhYWY5OWNlYjAiLCJpaWQiOjQ1ODkwNDkwLCJvaWQiOjEzNjkyOTUsInMiOjEwMjIsInNpZCI6ImM3ODI4Njk4LThlOTktNGVmYi1iODcxLTk1ZjhlODMxMmMxNCIsInQiOmZhbHNlLCJ1aWQiOjQ1ODkwNDkwfQ.CMANS9L1vyRE450nMrp4m8ZjjDFKhWiMtnN-DuuWvQ_uMn2bjeqm4pIDFTCpVMOqhulV5N8ykQSpdyFfE_RguA'
WILDBERRIES_API_URL = 'https://marketplace-api.wildberries.ru/api/v3/orders/new'


class ItemService:
    @staticmethod
    def get_all() -> list[Item]:
        return ItemRepository.get_all()

    @staticmethod
    def insert(article: str, qrcode: str) -> Optional[int]:
        return ItemRepository.insert(article, qrcode)

    @staticmethod
    def write_off(qrcode: str) -> Optional[int]:
        return ItemRepository.write_off(qrcode)

    @staticmethod
    def shipment(qrcode: str) -> Optional[int]:
        return ItemRepository.shipment(qrcode)

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
    def get_wildberries_orders(key: str) -> None:
        headers = {
            'Authorization': key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(WILDBERRIES_API_URL, headers=headers)
            response.raise_for_status()  # Вызвать ошибку для статусов 4xx/5xx

            data = response.json()  # Получаем список заказов как JSON-объект
            orders = data.get("orders", [])

            # Удаляем все существующие записи в таблице Item
            ItemRepository.delete_all()

            # Создаем словарь для подсчета количества товаров по article
            article_count = {}

            # Подсчитываем количество товаров по каждому article
            for order in orders:
                article = order.get("article")
                if article is not None:
                    # Увеличиваем счетчик для данного article
                    if article in article_count:
                        article_count[article] += 1
                    else:
                        article_count[article] = 1

            # Сохраняем данные в базу данных
            for article, count in article_count.items():
                # Создаем новый объект
                ItemService.insert(article, count)

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        except Exception as err:
            logging.error(f"An error occurred: {err}")

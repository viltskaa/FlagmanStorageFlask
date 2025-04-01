from datetime import datetime
from typing import Optional
from urllib.parse import quote
import requests
from .shipment_item_service import ShipmentItemService
from .token_service import TokenService

from datetime import datetime, timezone, timedelta

class WBService:
    BASE_URL = "https://marketplace-api.wildberries.ru/api/v3/orders"
    STICKERS_URL = "https://marketplace-api.wildberries.ru/api/v3/orders/stickers"
    STATUS_URL = "https://marketplace-api.wildberries.ru/api/v3/orders/status"
    SUPPLY_ADD_URL = "https://marketplace-api.wildberries.ru/api/v3/supplies"
    SUPPLY_ADD_ORDER_URL = "https://marketplace-api.wildberries.ru/api/v3/supplies/{supplyId}/orders/{orderId}"
    SUPPLY_QR_URL = "https://marketplace-api.wildberries.ru/api/v3/supplies/{supplyId}/barcode"
    @staticmethod
    def get_sticker(order: int) -> str | None:
        wb_url = WBService.STICKERS_URL
        response = None
        print(order)
        try:
            tokens = TokenService.get_tokens()
            for token in tokens:
                headers = {
                    'Authorization': token.token,
                    'Content-Type': 'application/json'
                }
                params = {
                    "type": "png",
                    "width": 40,
                    "height": 30,
                }
                body = {
                    "orders": [order]
                }
                response = requests.post(wb_url, headers=headers, json=body,params=params)
                response.raise_for_status()
                data = response.json()
                stickers = data.get("stickers", [])
                if len(stickers) == 0:
                    continue

                for sticker in stickers:
                    return sticker

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            if response is not None:
                error_message += f" - Response: {response.text}"
            raise Exception(error_message)

        except Exception as err:
            raise Exception(f"An error occurred: {err}")

    @staticmethod
    def get_supply_qr(supply_id: int) -> Optional[str]:
        # Кодируем supply_id для корректной вставки в URL
        encoded_supply_id = quote(str(supply_id))
        url = WBService.SUPPLY_QR_URL.format(supplyId=encoded_supply_id)

        response = None
        try:
            tokens = TokenService.get_tokens()
            for token in tokens:
                headers = {
                    'Authorization': token.token,
                    'Content-Type': 'application/json'
                }
                params = {
                    "type": "png",
                }
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()

                # Проверяем ответ
                data = response.json()
                qr_code = data.get("file")
                if qr_code:
                    return qr_code

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            if response is not None:
                error_message += f" - Response: {response.text}"
            raise Exception(error_message)

        except Exception as err:
            raise Exception(f"An error occurred: {err}")

    @staticmethod
    def create_supply(token_name:str) -> str | None:
        wb_url = WBService.SUPPLY_ADD_URL
        response = None
        token = TokenService.get_token_by_name(token_name)
        today_date = datetime.now().strftime("%d_%m_%Y")
        name = f"{token_name}_{today_date}"
        try:
            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }
            body = {
                "name": name
            }
            response = requests.post(wb_url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            id = data.get("id", "")
            return id
        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            if response is not None:
                error_message += f" - Response: {response.text}"
            raise Exception(error_message)

        except Exception as err:
            raise Exception(f"An error occurred: {err}")

    @staticmethod
    def add_to_supply(supply_id: str, orders_ids: list[int], token:str):
        response = None
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }

        try:
            for order_id in orders_ids:
                wb_url = WBService.SUPPLY_ADD_ORDER_URL.format(supplyId=supply_id, orderId=order_id)
                response = requests.post(wb_url, headers=headers)
                response.raise_for_status()
                data = response.json()

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            if response is not None:
                error_message += f" - Response: {response.text}"
            raise Exception(error_message)

        except Exception as err:
            raise Exception(f"An error occurred: {err}")





    @staticmethod
    def fetch_orders_for_all():
        tokens = TokenService.get_tokens()
        for item in tokens:
            id = item.name
            #WBService.create_supply(item.name)
            WBService.fetch_orders(item.name,id)

    @staticmethod
    def fetch_orders(name: str,supply_id:str):
        try:
            token = TokenService.get_token_by_name(name)
            if not token:
                raise Exception(f"Token with name '{name}' not found in database")

            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }

            now = datetime.now()
            time_range = {
                "dateFrom": int(
                    (now.replace(hour=19, minute=0, second=0, microsecond=0) - timedelta(days=1)).timestamp()),
                "dateTo": int(now.replace(hour=6, minute=0, second=0, microsecond=0).timestamp())
            }

            params = {
                "limit": 1000,
                "next": 0,
                "dateFrom": time_range["dateFrom"],
                "dateTo": time_range["dateTo"]
            }

            response = requests.get(WBService.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            all_orders = data.get("orders", [])

            if not all_orders:
                return

            order_ids = [order.get("id") for order in all_orders]
            print(order_ids)

            status_response = requests.post(WBService.STATUS_URL, json={"orders": order_ids}, headers=headers)
            status_response.raise_for_status()
            status_data = status_response.json()
            status_orders = {order["id"]: order for order in status_data.get("orders", [])}
            orders_ids = []
            for order in all_orders:
                order_id = order.get("id")
                order_status = status_orders.get(order_id, {}).get("supplierStatus")
                order_supply_id = order.get("supplyId")
                orders_ids.append(order_id)
                if order_status == "complete" and order_supply_id != "":
                    ShipmentItemService.insert(
                        order_id,
                        order.get("article"),
                        order.get("orderUid"),
                        datetime.now(),
                        "RECEIVED",
                        name,
                        order.get("supplyId")
                    )
            #WBService.add_to_supply(supply_id,orders_ids,token)
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request error: {req_err}")
        except Exception as err:
            raise Exception(f"An error occurred: {err}")




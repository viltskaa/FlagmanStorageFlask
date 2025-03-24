from datetime import datetime
import requests
from .shipment_item_service import ShipmentItemService
from .token_service import TokenService

from datetime import datetime, timezone, timedelta

class WBService:
    BASE_URL = "https://marketplace-api.wildberries.ru/api/v3/orders"
    STICKERS_URL = "https://marketplace-api.wildberries.ru/api/v3/orders/stickers"
    STATUS_URL = "https://marketplace-api.wildberries.ru/api/v3/orders/status"

    @staticmethod
    def get_sticker(order: int) -> str | None:
        wb_url = WBService.STICKERS_URL
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
    def fetch_orders_for_all():
        tokens = TokenService.get_tokens()
        for item in tokens:
            WBService.fetch_orders(item.name)

    @staticmethod
    def fetch_orders(name: str):
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
                "limit": 100,
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

            for order in all_orders:
                order_id = order.get("id")
                order_status = status_orders.get(order_id, {}).get("supplierStatus")
                print(order_status)
                if order_status == "complete":
                    ShipmentItemService.insert(
                        order_id,
                        order.get("article"),
                        order.get("orderUid"),
                        datetime.now(),
                        "RECEIVED",
                        name
                    )
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request error: {req_err}")
        except Exception as err:
            raise Exception(f"An error occurred: {err}")




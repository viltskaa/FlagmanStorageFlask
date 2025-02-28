from datetime import datetime
import requests
from .shipment_item_service import ShipmentItemService
from .token_service import TokenService


class WBService:
    BASE_URL = "https://marketplace-api.wildberries.ru/api/v3/orders/new"

    @staticmethod
    def fetch_orders(name: str):
        wb_url = WBService.BASE_URL
        response = None

        try:
            token = TokenService.get_token_by_name(name)
            if not token:
                raise Exception(f"Token with name '{name}' not found in database")

            headers = {
                'Authorization': token,
                'Content-Type': 'application/json'
            }

            response = requests.get(wb_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            orders = data.get("orders", [])

            for order in orders:
                ShipmentItemService.insert(order.get("article"), order.get("orderUid"), datetime.now(), 'RECEIVED', name)

        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err}"
            if response is not None:
                error_message += f" - Response: {response.text}"
            raise Exception(error_message)

        except Exception as err:
            raise Exception(f"An error occurred: {err}")
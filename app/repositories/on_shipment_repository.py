from typing import Optional
from flask import current_app
from datetime import datetime
from app.database import database as db

class OnShipmentRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def get_shipment_id_by_qrcode(qrcode: str) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute("SELECT shipment_id FROM on_shipment WHERE qrcode = ?", (qrcode,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            OnShipmentRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def check_qrcode_not_exists(qrcode: str) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute("SELECT id FROM on_shipment WHERE qrcode = ?", (qrcode,))
            return cursor.fetchone() is None
        except Exception as e:
            OnShipmentRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def insert(shipment_id: int, qrcode: str) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(
                "INSERT INTO on_shipment (shipment_id, qrcode) VALUES (?, ?)",
                (shipment_id, qrcode),
            )
            database.commit()
            return cursor.lastrowid  # Возвращаем ID новой записи
        except Exception as e:
            OnShipmentRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def remove_if_ids(shipments_ids: list[int]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(f'''
                                DELETE FROM on_shipment WHERE shipment_id IN ({','.join(['?'] * len(shipments_ids))})
                               ''', shipments_ids,)
            database.commit()
            return True
        except Exception as e:
            OnShipmentRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def get_qrCodes(shipments_ids: list[int]) -> list[str]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(f'''
                                   SELECT qrcode
                                   FROM on_shipment
                                   WHERE shipment_id IN ({','.join(['?'] * len(shipments_ids))})
                               ''', shipments_ids,)
            qr_codes = [row[0] for row in cursor.fetchall()]
            print(True)
            return qr_codes
        except Exception as e:
            OnShipmentRepository.last_error = e
            current_app.logger.error(e)
            print(False)
            return []
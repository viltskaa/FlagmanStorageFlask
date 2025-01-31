from typing import Optional
from flask import current_app
from datetime import datetime
from app.database import database as db

class OnShipmentRepository:
    last_error: Optional[Exception] = None

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
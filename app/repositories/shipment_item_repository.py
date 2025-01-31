from typing import Optional
from flask import current_app
from app.database import ShipmentItem
from datetime import datetime
from app.database import database as db

class ShipmentItemRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def insert(article: str, count_all: int, date: datetime) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                """
                INSERT INTO shipment_item (article, count_cur, count_all, created_at, is_active)
                VALUES (?, 0, ?, ?, 0)
                """,
                (article, count_all, date)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_all() -> list[ShipmentItem]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute('''
                            SELECT id, article, count_cur, count_all, worker_id, created_at, is_active
                            FROM shipment_item
                            WHERE DATE(created_at) = ? AND is_active = 0
                        ''', (today_date,))
            rows = cursor.fetchall()
            return [ShipmentItem(*row) for row in rows]
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def check_all_count_cur_equals_count_all():
        items = ShipmentItemRepository.get_all()
        if len(items) == 0:
            return False
        for item in items:
            # Accessing the attributes using dot notation
            if item.count_cur != item.count_all:
                return False
        return True

    @staticmethod
    def get_active_shipment_by_article(article: str):
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(
                """SELECT id, article, count_cur, count_all 
                   FROM shipment_item 
                   WHERE article = ? AND is_active = 0 
                   AND DATE(created_at) = DATE('now')""",
                (article,),
            )
            row = cursor.fetchone()
            return ShipmentItem(*row) if row else None
        except Exception as e:
            current_app.logger.error(e)
            return None

    @staticmethod
    def update_count_cur(shipment_id: int, new_count_cur: int) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(
                "UPDATE shipment_item SET count_cur = ? WHERE id = ?",
                (new_count_cur, shipment_id),
            )
            database.commit()
            return cursor.rowcount > 0
        except Exception as e:
            current_app.logger.error(e)
            return False




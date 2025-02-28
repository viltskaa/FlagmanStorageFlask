import json
from typing import Optional
from flask import current_app
from app.database import ShipmentItem
from datetime import datetime
from app.database import database as db

class ShipmentItemRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def get_by_id(id: int) -> Optional[ShipmentItem]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('''
                SELECT id, article, count_cur, count_all,for_this, worker_id, created_date, created_time, is_active
                FROM shipment_item
                WHERE id = ?
            ''', (id,))
            row = cursor.fetchone()
            if row:
                return ShipmentItem(*row)
            return None
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def insert(article: str, order_id: str, date: datetime, status: str, for_this: str, worker_id: int = None) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                """
                INSERT INTO shipment_item (article, orderUid, worker_id, created_date, created_time, 
                is_active, for_this)
                VALUES (?, ?, ?, DATE(?), TIME(?), ?,?)
                """,
                (article, order_id, worker_id, date, date, status, for_this)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_all(tokens: list[str]) -> list[dict]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(f'''
                SELECT orderUid, 
                       json_group_array(
                           json_object(
                               'id', id,
                               'article', article,
                               'worker_id', worker_id,
                               'created_date', created_date,
                               'created_time', created_time,
                               'is_active', is_active,
                               'scanned', scanned,
                               'for_this', for_this
                           )
                       ) AS items
                FROM shipment_item
                WHERE created_date = ? 
                  AND for_this IN ({','.join(['?'] * len(tokens))})  
                  AND (is_active = 'RECEIVED' OR is_active = 'POSTPONED')
                GROUP BY orderUid
                ORDER BY COUNT(*) ASC
            ''', (today_date, *tokens,))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                order_uid, items_json = row
                result.append({
                    "orderUid": order_uid,
                    "items": json.loads(items_json),
                })

            return result
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def get_all_by_period(date_start: datetime, date_end: datetime, status: str) -> list[ShipmentItem]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            date_start_datetime = date_start.strftime("%Y-%m-%d %H:%M:%S")
            date_end_datetime = date_end.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                    SELECT id, article, count_cur,count_all,for_this,worker_id,created_date, created_time 
                    FROM shipment_item 
                    WHERE is_active = ?
                    AND (created_date || ' ' || created_time) BETWEEN ? AND ?
                """, (status, date_start_datetime, date_end_datetime))
            rows = cursor.fetchall()
            return [ShipmentItem(*row) for row in rows]
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def check_all_count_cur_equals_count_all(tokens: list[str]):
        items = ShipmentItemRepository.get_all(tokens)
        if not items:
            return False
        return all(item.count_cur == item.count_all for item in items)

    @staticmethod
    def get_active_shipment_by_article(article: str, tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""SELECT id, article, orderUid, scanned, for_this 
                   FROM shipment_item 
                   WHERE article = ?  AND for_this IN ({','.join(['?'] * len(tokens))}) AND (is_active = 'RECEIVED' OR is_active = 'POSTPONED') 
                   and scanned = 'NOTSCANNED'
                   AND created_date = ?""",
                (article, *tokens, today_date),
            )
            row = cursor.fetchone()
            return ShipmentItem(*row) if row else None
        except Exception as e:
            current_app.logger.error(e)
            return None

    @staticmethod
    def update_scanned(shipment_id: int,user_id: int) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(
                "UPDATE shipment_item SET scanned = 'SCANNED', worker_id=? WHERE id = ?",
                (user_id, shipment_id),
            )
            database.commit()
            return cursor.rowcount > 0
        except Exception as e:
            current_app.logger.error(e)
            return False

    @staticmethod
    def delete(id: int):
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('''
                DELETE FROM shipment_item
                WHERE id = ?
            ''', (id,))

            database.commit()
            return True
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(f"Ошибка удаления: {e}")
            return False

    @staticmethod
    def update_count_all(item_id: int, count_all: int,worker_id: int) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute('''
                UPDATE shipment_item
                SET count_all = ?, worker_id = ?
                WHERE id = ? AND is_active = 'RECEIVED'
            ''', (count_all,worker_id, item_id))

            database.commit()
            return True
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(f"Ошибка обновления count_all: {e}")
            return False

    @staticmethod
    def update_today(user_id: int):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute('''
                UPDATE shipment_item
                SET is_active = 'SHIPPED',worker_id=?
                WHERE created_date = ? AND count_cur = count_all
            ''', (user_id, today_date,))
            database.commit()
            return True
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(f"Ошибка обновления is_active: {e}")
            return False

    @staticmethod
    def get_all_true() -> list[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute('''
                SELECT id
                FROM shipment_item
                WHERE created_date = ? AND is_active = 'SHIPPED'
            ''', (today_date,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []






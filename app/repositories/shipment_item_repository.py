import json
from typing import Optional
from flask import current_app
from app.database import ShipmentItem
from datetime import datetime, timedelta
from app.database import database as db

class ShipmentItemRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def get_order_id(id: int) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute("SELECT order_id FROM shipment_item WHERE id = ?", (id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return None


    @staticmethod
    def insert(shipment_id: int, article: str, order_id: str, date: datetime, status: str, for_this: str, supply_id :str,worker_id: int = None) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                """
                INSERT INTO shipment_item (order_id, article, orderUid, worker_id, created_date, created_time, 
                is_active, for_this,supply_id)
                VALUES (?, ?, ?, ?, DATE(?), TIME(?), ?,?,?)
                """,
                (shipment_id, article, order_id, worker_id, date, date, status, for_this,supply_id)
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
                ORDER BY scanned_time DESC
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
    def get_all_to_ship(tokens: list[str]) -> list[dict]:
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
                      AND (is_active = 'TO_SHIP')
                    GROUP BY orderUid
                    ORDER BY scanned_time DESC
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
    def is_order_fully_scanned(tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()

            today_date = datetime.now().strftime('%Y-%m-%d')  # Текущая дата

            cursor.execute(
                f"""SELECT COUNT(*) 
                    FROM shipment_item si
                    WHERE si.for_this IN ({','.join(['?'] * len(tokens))})
                    AND si.is_active IN ('RECEIVED', 'POSTPONED')  -- Статусы RECEIVED или POSTPONED
                    AND si.scanned = 'SCANNED'  -- Все записи должны быть отсканированы
                    AND DATE(si.created_date) = ?  -- Только за сегодняшний день
                """,
                (*tokens, today_date)
            )
            scanned_count = cursor.fetchone()[0]

            cursor.execute(
                f"""SELECT COUNT(*)
                    FROM shipment_item si
                    WHERE si.for_this IN ({','.join(['?'] * len(tokens))})
                    AND si.is_active IN ('RECEIVED', 'POSTPONED')
                    AND DATE(si.created_date) = ?  -- Только за сегодняшний день
                """,
                (*tokens, today_date)
            )
            total_count = cursor.fetchone()[0]

            return scanned_count == total_count
        except Exception as e:
            current_app.logger.error(e)
            return False

    @staticmethod
    def is_orders_to_ship_fully_scanned(tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()

            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""SELECT COUNT(*) 
                    FROM shipment_item si
                    WHERE si.for_this IN ({','.join(['?'] * len(tokens))})
                    AND si.is_active = 'TO_SHIP'  -- Только записи с статусом TO_SHIP
                    AND si.scanned = 'SCANNED'  -- Все записи должны быть отсканированы
                    AND DATE(si.created_date) = ?  -- Только за сегодняшний день
                """,
                (*tokens, today_date)
            )
            scanned_count = cursor.fetchone()[0]

            cursor.execute(
                f"""SELECT COUNT(*)
                    FROM shipment_item si
                    WHERE si.for_this IN ({','.join(['?'] * len(tokens))})
                    AND si.is_active = 'TO_SHIP'
                    AND DATE(si.created_date) = ?
                """,
                (*tokens, today_date)
            )
            total_count = cursor.fetchone()[0]

            return scanned_count == total_count
        except Exception as e:
            current_app.logger.error(e)
            return False

    @staticmethod
    def get_all_by_period(date_start: datetime, date_end: datetime, status: str) -> list[ShipmentItem]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            date_start_datetime = date_start.strftime("%Y-%m-%d %H:%M:%S")
            date_end_datetime = date_end.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                    SELECT id, article, orderUid,for_this,scanned,supply_id,scanned_time,worker_id,created_date, created_time,action_time,is_active 
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
    def get_active_shipment_by_article(article: str, tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""SELECT si.id, si.article, si.orderUid, si.for_this, si.scanned,si.supply_id, si.scanned_time, COUNT(DISTINCT si2.article) AS unique_products_count
                   FROM shipment_item si
                   LEFT JOIN shipment_item si2 ON si.orderUid = si2.orderUid
                   WHERE si.article = ?  
                   AND si.for_this IN ({','.join(['?'] * len(tokens))})
                   AND (si.is_active = 'RECEIVED' OR si.is_active = 'POSTPONED') 
                   AND si.scanned = 'NOTSCANNED'
                   AND si.created_date = ?
                   GROUP BY si.orderUid, si.id, si.article, si.for_this, si.scanned, si.scanned_time
                   ORDER BY unique_products_count ASC
                   LIMIT 1""",
                (article, *tokens, today_date),
            )
            row = cursor.fetchone()
            return ShipmentItem(*row) if row else None
        except Exception as e:
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_active_to_shipment_by_article(article: str, tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""SELECT si.id, si.article, si.orderUid, si.for_this, si.scanned,si.supply_id, si.scanned_time, COUNT(DISTINCT si2.article) AS unique_products_count
                       FROM shipment_item si
                       LEFT JOIN shipment_item si2 ON si.orderUid = si2.orderUid
                       WHERE si.article = ?  
                       AND si.for_this IN ({','.join(['?'] * len(tokens))})
                       AND (si.is_active = 'TO_SHIP') 
                       AND si.scanned = 'NOTSCANNED'
                       AND si.created_date = ?
                       GROUP BY si.orderUid, si.id, si.article, si.for_this, si.scanned, si.scanned_time
                       ORDER BY unique_products_count ASC
                       LIMIT 1""",
                (article, *tokens, today_date),
            )
            row = cursor.fetchone()
            return ShipmentItem(*row) if row else None
        except Exception as e:
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_active_to_shipment_by_id_and_tokens(shipment_id: int, tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""SELECT si.id, si.article, si.orderUid, si.for_this, si.scanned, si.supply_id, si.scanned_time, 
                          COUNT(DISTINCT si2.article) AS unique_products_count
                   FROM shipment_item si
                   LEFT JOIN shipment_item si2 ON si.orderUid = si2.orderUid
                   WHERE si.id = ?  
                   AND si.for_this IN ({','.join(['?'] * len(tokens))})
                   AND (si.is_active = 'TO_SHIP') 
                   AND si.scanned = 'NOTSCANNED'
                   AND si.created_date = ?
                   GROUP BY si.orderUid, si.id, si.article, si.for_this, si.scanned, si.scanned_time
                   ORDER BY unique_products_count ASC
                   LIMIT 1""",
                (shipment_id, *tokens, today_date),
            )
            row = cursor.fetchone()
            return ShipmentItem(*row) if row else None
        except Exception as e:
            current_app.logger.error(f"Ошибка в get_active_to_shipment_by_id_and_tokens: {e}")
            return None

    @staticmethod
    def update_scanned(shipment_id: int,user_id: int) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute("SELECT scanned FROM shipment_item WHERE id = ?", (shipment_id,))
            row = cursor.fetchone()

            if row and row[0] == 'SCANNED':
                return False

            today_date = datetime.now()
            cursor.execute(
                "UPDATE shipment_item SET scanned = 'SCANNED', worker_id=?, scanned_time = ? WHERE id = ?",
                (user_id, today_date, shipment_id),
            )
            database.commit()

            return cursor.rowcount > 0
        except Exception as e:
            current_app.logger.error(e)
            return False


    @staticmethod
    def update_status_of_ids(shipments_ids: list[int]) -> bool:
        if not shipments_ids:
            return False  # Защита от пустого списка

        try:
            today_date = "0000-12-31 00:00:00"
            database = db.get_database()
            cursor = database.cursor()

            query = f'''UPDATE shipment_item 
                        SET scanned = 'NOTSCANNED', scanned_time = ?  
                        WHERE id IN ({','.join(['?'] * len(shipments_ids))})'''

            cursor.execute(query, [today_date] + shipments_ids)

            database.commit()
            return True
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
    def get_ids_of_partially_scanned_items(user_id: int):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            query = """
                        SELECT si.id
                        FROM shipment_item si
                        WHERE si.created_date = ?
                        AND si.is_active IN ('RECEIVED', 'POSTPONED') 
                        AND si.scanned = 'SCANNED'
                        AND si.orderUid IN (
                            SELECT si2.orderUid
                            FROM shipment_item si2
                            WHERE  si2.created_date = ?
                            AND si2.is_active IN ('RECEIVED', 'POSTPONED')
                            GROUP BY si2.orderUid
                            HAVING COUNT(CASE WHEN si2.scanned = 'SCANNED' THEN 1 END) > 0
                            AND COUNT(CASE WHEN si2.scanned != 'SCANNED' THEN 1 END) > 0
                        )
                    """

            cursor.execute(query, (today_date, today_date))
            ids = [row[0] for row in cursor.fetchall()]
            return ids

        except Exception as e:
            current_app.logger.error(f"Database error: {e}")
            return []

    @staticmethod
    def update_not_scanned(orderUid: str) -> bool:
        try:
            today_date = "0000-12-31 00:00:00"
            database = db.get_database()
            cursor = database.cursor()

            query = '''UPDATE shipment_item 
                            SET scanned = 'NOTSCANNED', scanned_time = ?  
                            WHERE orderUid = ?'''

            cursor.execute(query, (today_date,orderUid))

            database.commit()
            return True
        except Exception as e:
            current_app.logger.error(e)
            return False

    @staticmethod
    def stock(orderUid: str,worker_id:int) -> bool:
        try:
            date = "0000-12-31 00:00:00"
            tomorrow = datetime.now() + timedelta(days=1)
            database = db.get_database()
            cursor = database.cursor()

            query = '''UPDATE shipment_item 
                                SET scanned = 'NOTSCANNED', worker_id = ?, is_active = 'POSTPONED',
                                created_date = ?, scanned_time = ?  
                                WHERE orderUid = ? AND is_active='RECEIVED' '''

            cursor.execute(query, (worker_id, tomorrow, date, orderUid))

            database.commit()
            return True
        except Exception as e:
            current_app.logger.error(e)
            return False

    @staticmethod
    def get_by_orderUid(orderUid: str) -> list[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('''
                    SELECT id
                    FROM shipment_item
                    WHERE orderUid = ?
                ''', (orderUid,))
            rows = cursor.fetchall()
            if rows:
                return [row[0] for row in rows]
            return []
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def update_status_of_fully_scanned_items(user_id: int,tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            # Обновляем статус is_active
            cursor.execute(
                f"""UPDATE shipment_item
                   SET is_active = 'TO_SHIP', worker_id = ?, action_time = ?
                   WHERE created_date = ?
                   AND is_active IN ('RECEIVED', 'POSTPONED')
                   AND si.for_this IN ({','.join(['?'] * len(tokens))})
                   AND orderUid IN (
                        SELECT si.orderUid
                        FROM shipment_item si
                        WHERE si.created_date = ?
                        GROUP BY si.orderUid
                        HAVING COUNT(si.id) = SUM(CASE WHEN si.scanned = 'SCANNED' THEN 1 ELSE 0 END)
                    )
                   RETURNING id""",
                (user_id, today_date, today_date,*tokens, today_date)
            )

            updated_ids = [row[0] for row in cursor.fetchall()]
            print("Обновленные ID:", updated_ids)

            if updated_ids:
                cursor.execute(
                    """UPDATE shipment_item
                       SET scanned = 'NOTSCANNED'
                       WHERE id IN ({})""".format(",".join(map(str, updated_ids)))
                )

            database.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error updating shipment items: {e}")
            return False

    @staticmethod
    def get_unique_supply_ids(ids: list[int]) -> list[str]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            # Извлекаем уникальные supply_id для переданных ID
            cursor.execute(
                """SELECT DISTINCT supply_id
                   FROM shipment_item
                   WHERE id IN ({})""".format(",".join(map(str, ids))),
            )

            # Получаем список уникальных supply_id
            supply_ids = [row[0] for row in cursor.fetchall()]
            return supply_ids
        except Exception as e:
            current_app.logger.error(f"Ошибка при получении уникальных supply_id: {e}")
            return []

    @staticmethod
    def update_status_for_today_shipment_items(tokens: list[str]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute(
                f"""UPDATE shipment_item
                   SET is_active = 'SHIPPED', scanned = 'NOTSCANNED', action_time = ?
                   WHERE created_date = ?
                   AND is_active = 'TO_SHIP'
                   AND scanned = 'SCANNED'
                   AND for_this IN ({','.join(['?'] * len(tokens))})
                   RETURNING id""",
                (today_date, today_date, *tokens)
            )

            updated_ids = [row[0] for row in cursor.fetchall()]
            print("Обновленные ID:", updated_ids)

            database.commit()
            return updated_ids
        except Exception as e:
            current_app.logger.error(f"Error updating shipment items: {e}")
            return []

    @staticmethod
    def get_all_true(user_id: int) -> list[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            today_date = datetime.now().strftime('%Y-%m-%d')

            cursor.execute('''
                SELECT id
                FROM shipment_item
                WHERE created_date = ? AND is_active = 'TO_SHIP' AND worker_id = ?
            ''', (today_date, user_id,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            ShipmentItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    def check(id: int) -> bool:
        database = db.get_database()
        cursor = database.cursor()
        cursor.execute('''
        SELECT CASE WHEN is_active = 'TO_SHIP' THEN 1 ELSE 0 END FROM shipment_item WHERE id = ?
        ''', (id,))

        result = cursor.fetchone()
        if result is None:
            return False

        if result[0] == 1:
            return True
        else:
            return False





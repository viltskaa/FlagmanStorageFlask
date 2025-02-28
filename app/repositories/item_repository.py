from datetime import datetime
from typing import Optional

from flask import current_app
from app.database import Item

from app.database import database as db


class ItemRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def get_all() -> list[Item]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute("SELECT id, article, qrcode FROM item WHERE status = 'STORAGE'")
            rows = cursor.fetchall()
            return [Item(*row) for row in rows]
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def get_all_by_period(date_start: datetime,date_end: datetime,status: str) -> list[Item]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            date_start_datetime = date_start.strftime("%Y-%m-%d %H:%M:%S")
            date_end_datetime = date_end.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT id, article, qrcode 
                FROM item 
                WHERE status = ?
                AND (created_date || ' ' || created_time) BETWEEN ? AND ?
            """, (status,date_start_datetime, date_end_datetime))
            rows = cursor.fetchall()
            return [Item(*row) for row in rows]
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def delete_all() -> None:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('DELETE FROM item')
            database.commit()

        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def delete_by_id(item_id: int) -> None:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('DELETE FROM item WHERE id = ?', (item_id,))
            database.commit()
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def insert(article: str, qrcode: str, id: int) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                "INSERT INTO item (article, qrcode, status, worker_id) VALUES (?, ?, 'STORAGE',?)",
                (article, qrcode, id)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def write_off(qrcode: str,user_id:int) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute("UPDATE item SET status = 'WRITEOFF' , worker_id = ? WHERE qrcode = ? AND status = 'STORAGE'", (user_id,qrcode,))
            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def refund(qrcode: str, user_id: int) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                "UPDATE item SET status = 'REFUND' , worker_id = ? WHERE qrcode = ? AND (status = 'SHIPMENT' or "
                "status = 'WRITEOFF')",
                (user_id, qrcode,))
            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_by_article(article: str) -> Optional[Item]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id, article, qrcode FROM item WHERE article = ?', (article,))
            row = cursor.fetchone()
            if row:
                return Item(*row)
            else:
                return None
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def check_if_exists(qrcode: str) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id FROM item WHERE qrcode = ?', (qrcode,))
            row = cursor.fetchone()
            if row:
                return True
            else:
                return False
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def check_if_exists_and_status(qrcode: str) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id FROM item WHERE qrcode = ? AND status = "STORAGE"', (qrcode,))
            row = cursor.fetchone()
            if row:
                print(row[0])
                return True
            return False
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def check_if_exists_and_status_write_off(qrcode: str) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id FROM item WHERE qrcode = ? AND (status = "WRITEOFF" OR status = "SHIPMENT")',
                           (qrcode,))
            row = cursor.fetchone()
            if row:
                print(row[0])
                return True
            return False
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def shipment(qrcodes: list[str],worker_id: int) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(f'''
                        UPDATE item 
                        SET status = 'SHIPMENT', worker_id = ? 
                        WHERE qrcode IN ({','.join(['?'] * len(qrcodes))})
                    ''', (worker_id, *qrcodes))
            database.commit()
            print(True)
            return True
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            print(False)
            return False
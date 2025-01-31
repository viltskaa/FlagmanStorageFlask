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
    def insert(article: str, qrcode: str) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                "INSERT INTO item (article, qrcode, status) VALUES (?, ?, 'STORAGE')",
                (article, qrcode)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def write_off(qrcode: str) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute("UPDATE item SET status = 'WRITEOFF' WHERE qrcode = ? AND status = 'STORAGE'", (qrcode,))
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
            return bool(cursor.fetchone())
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return False

    @staticmethod
    def shipment(qrcodes: list[str]) -> bool:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(f'''
                        UPDATE item SET status = 'SHIPMENT' WHERE qrcode IN ({','.join(['?'] * len(qrcodes))})
                    ''', qrcodes)
            database.commit()
            print(True)
            return True
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            print(False)
            return False
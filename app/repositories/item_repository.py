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
            cursor.execute('SELECT id, article, count FROM item')
            rows = cursor.fetchall()
            return [Item(*row) for row in rows]
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None
                
    
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
            cursor.execute('DELETE FROM items WHERE id = ?', (item_id))
            database.commit()
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None

        

    @staticmethod
    def insert(article: str, count: int) -> Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                'INSERT INTO item (article, count) VALUES (?, ?)',
                (article, count)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None       
            
            
    @staticmethod
    def get_by_article(article: str) -> Item:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id, article, count FROM items WHERE article = ?', (article))
            row = cursor.fetchone()
            if row:
                return Item(*row)
            else:
                return None
        except Exception as e:
            ItemRepository.last_error = e
            current_app.logger.error(e)
            return None


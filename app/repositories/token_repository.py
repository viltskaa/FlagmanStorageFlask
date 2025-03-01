from typing import Optional

from flask import current_app
from app.database import Item

from app.database import database as db
from app.database import Token


class TokenRepository:
    last_error: Optional[Exception] = None


    @staticmethod
    def get_token_by_name(name: str) -> Optional[str]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('''
                SELECT token
                FROM tokens
                WHERE name = ?
            ''', (name,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        except Exception as e:
            TokenRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def insert(name:str,token:str):
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                "INSERT INTO tokens (name, token) VALUES (?, ?)",
                (name, token)
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            TokenRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_all_tokens() -> list[Token]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute('SELECT id, name, token FROM tokens')
            rows = cursor.fetchall()
            if rows:
                return [Token(*row) for row in rows]
        except Exception as e:
            TokenRepository.last_error = e
            current_app.logger.error(e)
            return []
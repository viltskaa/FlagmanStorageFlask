from typing import Optional, List
from app.database import Worker
from flask import current_app

from app.database import database as db


class WorkerRepository:
    last_error: Optional[Exception] = None

    @staticmethod
    def get_all_users() -> list[Worker]:
        try:
            database = db.get_database()
            worker_rows = database.execute(
                'SELECT * FROM worker'
            ).fetchall()
            if worker_rows:
                return [Worker(*row) for row in worker_rows]
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_by_full_name(full_name: str) -> Optional[dict]:
        try:
            database = db.get_database()
            worker_row = database.execute(
                'SELECT * FROM worker WHERE full_name = ?', (full_name,)
            ).fetchone()

            if worker_row:
                worker = {
                    'id': worker_row[0],
                    'full_name':worker_row[1],
                    'password':worker_row[2]
                }
                return worker
            return None
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def get_tokens_ids(worker_id: int) -> list[int]:
        try:
            database = db.get_database()
            tokens = database.execute('SELECT token_id from worker_tokens WHERE worker_id = ?',(worker_id,)
            ).fetchall()
            return [row[0] for row in tokens]
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            return []

    @staticmethod
    def get_tokens(token_ids: list[int]) -> list[str]:
        try:
            database = db.get_database()
            cursor = database.cursor()
            cursor.execute(f'''
                                   SELECT name
                                   FROM tokens
                                   WHERE id IN ({','.join(['?'] * len(token_ids))})
                               ''', token_ids, )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            print(False)
            return []

    @staticmethod
    def insert(full_name: str, password: str) -> \
            Optional[int]:
        try:
            database = db.get_database()
            cursor = database.cursor()

            cursor.execute(
                'INSERT INTO worker (full_name,password) VALUES (?, ?)',
                (full_name,password, )
            )

            database.commit()
            return cursor.lastrowid
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            return None

    @staticmethod
    def insert_tokens(user_id: int, ids: List[int]):
        try:
            database = db.get_database()
            cursor = database.cursor()
            for id in ids:
                cursor.execute(
                    'INSERT INTO worker_tokens (worker_id,token_id) VALUES (?, ?)',
                    (user_id,id)
                )
            database.commit()
        except Exception as e:
            WorkerRepository.last_error = e
            current_app.logger.error(e)
            return None

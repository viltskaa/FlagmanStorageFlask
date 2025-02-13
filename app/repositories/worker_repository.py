from typing import Optional

from flask import current_app

from app.database import database as db


class WorkerRepository:
    last_error: Optional[Exception] = None

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


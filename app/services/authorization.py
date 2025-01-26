from typing import Optional

from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from app.repositories import WorkerRepository

bcrypt = Bcrypt()


class AuthorizationService:

    @staticmethod
    def register(name: str, surname: str, patronymic: str, password: str) -> Optional[int]:
        if not all([name, surname, password, patronymic]):
            return None

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        worker_id = WorkerRepository.insert(name, surname, patronymic, password_hash)

        if worker_id:
            return worker_id
        else:
            return None

    @staticmethod
    def login(name: str, surname: str, patronymic: str, password: str) -> Optional[str]:
        return "111"

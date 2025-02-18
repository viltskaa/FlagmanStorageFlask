from typing import Optional

from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from app.repositories import WorkerRepository

bcrypt = Bcrypt()


class AuthorizationService:

        @staticmethod
        def register(name: str, surname: str, patronymic: str, password: str) -> Optional[int]:
            if not all([name, surname, patronymic]):
                return None

            full_name = f"{surname} {name} {patronymic}"

            worker_id = WorkerRepository.insert(full_name,password)

            if worker_id:
                return worker_id
            else:
                return None

        @staticmethod
        def login(name: str, surname: str, patronymic: str, password: str) -> Optional[str]:
            full_name = f"{surname} {name} {patronymic}"
            worker = WorkerRepository.get_by_full_name(full_name)
            if worker:
                if worker['password'] == password:
                    access_token = create_access_token(identity=str(worker['full_name']))
                    return access_token
            return None
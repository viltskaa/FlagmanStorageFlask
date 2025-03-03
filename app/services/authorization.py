from typing import Optional, List

from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from app.repositories import WorkerRepository

bcrypt = Bcrypt()


class AuthorizationService:

        @staticmethod
        def register(name: str, surname: str, patronymic: str, password: str, ids: List[int],role:str) -> Optional[int]:
            if not all([name, surname, patronymic]):
                return None

            full_name = f"{surname} {name} {patronymic}"

            worker_id = WorkerRepository.insert(full_name,password,role)
            if worker_id:
                WorkerRepository.insert_tokens(worker_id,ids)
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

        @staticmethod
        def refresh(name: str, surname: str, patronymic: str):
            full_name = f"{surname} {name} {patronymic}"
            print(full_name)
            worker = WorkerRepository.get_by_full_name(full_name)
            if worker:
                access_token = create_access_token(identity=str(worker['full_name']))
                return access_token
            return None
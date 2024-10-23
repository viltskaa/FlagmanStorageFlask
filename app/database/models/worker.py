from dataclasses import dataclass


@dataclass
class Worker:
    id: int
    name: str
    surname: str
    patronymic: str
    password_hash: str

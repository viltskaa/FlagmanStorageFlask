from dataclasses import dataclass
from typing import List

@dataclass
class Worker:
    id: int
    name: str
    surname: str
    patronymic: str
    password_hash: str
    tokens: List[int]

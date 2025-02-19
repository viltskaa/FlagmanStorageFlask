from dataclasses import dataclass
from typing import List

@dataclass
class Worker:
    id: int
    full_name: str
    password: str

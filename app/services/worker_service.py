from typing import Optional

from app.repositories import WorkerRepository
from app.database import Worker
class WorkerService:
    @staticmethod
    def get_tokens(worker_id) -> list[str]:
        ids = WorkerRepository.get_tokens_ids(worker_id)
        tokens = WorkerRepository.get_tokens(ids)
        return tokens

    @staticmethod
    def get_workers() -> list[Worker]:
        return WorkerRepository.get_all_users()

    @staticmethod
    def get_worker(full_name) -> Optional[dict]:
        return WorkerRepository.get_by_full_name(full_name)

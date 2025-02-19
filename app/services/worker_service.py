from app.repositories import WorkerRepository

class WorkerService:
    @staticmethod
    def get_tokens(worker_id) -> list[str]:
        ids = WorkerRepository.get_tokens_ids(worker_id)
        tokens = WorkerRepository.get_tokens(ids)
        return tokens

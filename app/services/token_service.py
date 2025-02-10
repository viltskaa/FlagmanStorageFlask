from typing import Optional
from app.repositories import TokenRepository


class TokenService:

    @staticmethod
    def get_token_by_name(name: str) -> Optional[str]:
        return TokenRepository.get_token_by_name(name)

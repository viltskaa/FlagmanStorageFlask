from typing import Optional
from app.repositories import TokenRepository
from app.database import Token

class TokenService:

    @staticmethod
    def get_token_by_name(name: str) -> Optional[str]:
        return TokenRepository.get_token_by_name(name)

    @staticmethod
    def get_tokens() -> list[Token]:
        return TokenRepository.get_all_tokens()

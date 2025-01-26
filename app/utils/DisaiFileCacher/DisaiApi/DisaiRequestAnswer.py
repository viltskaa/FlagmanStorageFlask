from dataclasses import dataclass


@dataclass
class DisaiRequestAnswer:
    article: str
    gtin: int

    def to_csv(self) -> [str, int]:
        return [self.article, self.gtin]

    @staticmethod
    def from_csv(article: str, gtin: int):
        return DisaiRequestAnswer(article, gtin)

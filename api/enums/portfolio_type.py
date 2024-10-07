from enum import Enum


class PortfolioType(Enum):
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"

    def __str__(self) -> str:
        return f"{self.value}"

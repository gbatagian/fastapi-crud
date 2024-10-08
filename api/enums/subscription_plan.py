from enum import Enum


class SubscriptionPlan(Enum):
    FREEMIUM = "freemium"
    PREMIUM = "premium"
    GOLD = "gold"
    ULTRA = "ultra"

    def __str__(self) -> str:
        return f"{self.value}"

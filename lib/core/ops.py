from enum import StrEnum

class ComponentType(StrEnum):
    CHANNEL = "CHANNEL"
    FLASK = "FLASK"

    @property
    def key(self) -> str:
        return self.value


class ComponentName(StrEnum):
    STOCKAPI = "StockAPI"
    STOCKALERT = "StockAlert"

    @property
    def key(self) -> str:
        return self.value


class Customer(StrEnum):
    PLATFORM42 = "Platform42"

    @property
    def key(self) -> str:
        return self.value
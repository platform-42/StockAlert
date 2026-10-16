from enum import StrEnum

class ComponentType(StrEnum):
    CHANNEL = "CHANNEL"
    FLASK = "FLASK"

class ComponentName(StrEnum):
    STOCKAPI = "StockAPI"
    STOCKALERT = "StockAlert"

class Customer(StrEnum):
    PLATFORM42 = "Platform42"

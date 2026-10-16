from enum import StrEnum

class Argument(StrEnum):
    MONGODB = "--mongodb"
    STOCK_API = "--stock_api"
    STOCKS = "--stocks"
    APNS = "--apns"

    @property
    def key(self) -> str:
        return self.value
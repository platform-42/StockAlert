from enum import StrEnum

class HttpEndpoints(StrEnum):
    ALERTS_BY_SECTOR = "/2026-01/alerts/sector"
    DEVICES_DEREGISTER = "/2026-01/devices/deregister"
    DEVICES_REGISTER = "/2026-01/devices/register"
    QUOTES_BY_SECTOR = "/2026-01/quotes/sector"

    @property
    def key(self) -> str:
        return self.value

class QueryStringParam(StrEnum):
    SECTOR = "sector"

    @property
    def key(self) -> str:
        return self.value

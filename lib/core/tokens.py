from enum import StrEnum

class AppCFG(StrEnum):
    APNS = "apns"
    STOCKAPI = "stockapi"
    MONGO = "mongo"
    PERSISTENCE = "persistence"

    @property
    def key(self) -> str:
        return self.value

class JsonTKN(StrEnum):
    ACTION = "action"
    ALERT_TYPE = "alertType"
    ALERTS = "alerts"
    AVERAGE_VOLUME = "averageVolume"
    BREAKOUT_QUOTE = "breakoutQuote"
    CHANGE = "change"
    COLLAPSE_QUOTE = "collapseQuote"
    COUNT = "count"
    CREATED_AT = "createdAt"
    CURRENT_QUOTE = "currentQuote"
    CURRENT_VOLUME = "currentVolume"
    DATE = "date"
    DAYS_SINCE_YEAR_HIGH = "daysSinceYearHigh"
    DESCRIPTION = "description"
    DEVICE_ID = "deviceId"
    ID = "_id"
    LAST_ALERT_AT = "lastAlertAt"
    LAST_ALERT_QUOTE = "lastAlertQuote"
    LAST_UPDATED_AT = "lastUpdatedAt"
    MESSAGE = "message"
    MOVING_AVERAGE_10 = "movingAverage10"
    MOVING_AVERAGE_20 = "movingAverage20"
    MOVING_AVERAGE_30 = "movingAverage30"
    OPENING_QUOTE = "openingQuote"
    PRIO = "prio"
    PUSH_TOKEN = "pushToken"
    QUOTE = "quote"
    QUOTES = "quotes"
    REFERENCE = "ref"
    SECTOR = "sector"
    STATUS = "status"
    SUPPRESS_APNS = "suppressAPNS"
    TICKER = "ticker"
    TRADE_VALUE = "tradeValue"
    VOLUME = "volume"
    WARNING = "warning"
    YEAR_HIGH = "yearHigh"
    YEAR_LOW = "yearLow"

    @property
    def key(self) -> str:
        return self.value


class StocksCFG(StrEnum):
    BREAKOUT_QUOTE = "breakoutQuote"
    COLLAPSE_QUOTE = "collapseQuote"
    DESCRIPTION = "description"
    SECTOR = "sector"
    STOCKS = "stocks"
    TICKER = "ticker"

    @property
    def key(self) -> str:
        return self.value


class MongoCFG(StrEnum):
    COLLECTION_ALERTS = "collection_alerts"
    COLLECTION_DEVICES = "collection_devices"
    COLLECTION_QUOTES = "collection_quotes"
    DATABASE = "database"
    HOST = "host"
    PORT = "port"
    ROOT = "mongodb"
    URI = "uri"
    USER = "user"

    @property
    def key(self) -> str:
        return self.value


class YfinanceTKN(StrEnum):
    AVG_VOLUME_10DAY = "ten_day_average_volume"
    PREVIOUS_CLOSE = "regularMarketPreviousClose"
    CLOSE = "Close"
    LAST_PRICE = "last_price"
    LAST_VOLUME = "last_volume"
    OPEN = "open"
    VOLUME = "Volume"
    YEAR_HIGH = "yearHigh"
    YEAR_LOW = "yearLow"

    @property
    def key(self) -> str:
        return self.value


class APNSCFG(StrEnum):
    AUTH_KEY_FILEPATH = "auth_key_filepath"
    AUTH_KEY_ID = "auth_key_id"
    ROOT = "apns"
    SANDBOX = "sandbox"
    TEAM_ID = "team_id"
    TOPIC = "topic"

    @property
    def key(self) -> str:
        return self.value


class StockAPICFG(StrEnum):
    API_KEY = "api_key"
    HOST = "host"
    PORT = "port"
    ROOT = "stock_api"
    SERVER = "server"
    SSL_CERTFILE = "ssl_certfile"
    SSL_KEYFILE = "ssl_keyfile"

    @property
    def key(self) -> str:
        return self.value

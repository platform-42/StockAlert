from typing import (
    Dict,
    Optional,
    Mapping,
    Any,
    List,
    Callable,
    TypedDict
)
from lib.core.tokens import JsonTKN
from lib.alerts.rules import (
    volume_rule,
    bottom_rule,
    rise_rule,
    fall_rule
)

def fmt(
    value: float,
    decimals: int = 1
) -> str:
    return f"{value:.{decimals}f}"


MessageBuilder = Callable[
    [str, str, Mapping[str, Any]],
    str
]


class AlertTypeConfig(TypedDict):
    priority: int
    msg: MessageBuilder


def msg_volume(
    ticker: str,
    cur: float,
    rule_result: Dict[str, Any]
) -> str:
    trade_value = rule_result[JsonTKN.TRADE_VALUE.key]
    return f"{ticker} volume spike | value ${trade_value:,.0f} | now={cur}"


def msg_bottom(
    ticker: str,
    current: float,
    rule_result: Dict[str, Any]
) -> str:
    ref = rule_result[JsonTKN.REFERENCE.key]
    return f"{ticker} within 10% of 52-week low {fmt(ref)} | now={current}"


def msg_rise(
    ticker: str,
    current: float,
    rule_result: Dict[str, Any]
) -> str:
    ref = rule_result[JsonTKN.REFERENCE.key]
    return f"{ticker} rose 5% above last alert {fmt(ref)} | now={current}"


def msg_fall(
    ticker: str,
    current: float,
    rule_result: Dict[str, Any]
) -> str:
    ref = rule_result[JsonTKN.REFERENCE.key]
    return f"{ticker} fell 5% below last alert {fmt(ref)} | now={current}"


ALERT_TYPES: Dict[str, AlertTypeConfig] = {
    "FALL": {
        JsonTKN.PRIO.key: 80,
        JsonTKN.MESSAGE.key: msg_fall
    },
    "RISE": {
        JsonTKN.PRIO.key: 70,
        JsonTKN.MESSAGE.key: msg_rise
    },
    "VOLUME": {
        JsonTKN.PRIO.key: 60,
        JsonTKN.MESSAGE.key: msg_volume
    },
    "BOTTOM": {
        JsonTKN.PRIO.key: 50,
        JsonTKN.MESSAGE.key: msg_bottom
    },
}


def build_alert(
    quote: Mapping[str, Any],
    rule_result: Mapping[str, Any]
) -> Optional[Dict[str, Any]]:

    ticker: str = quote[JsonTKN.TICKER.key]
    current: float = quote[JsonTKN.CURRENT_QUOTE.key]
    volume: int = quote[JsonTKN.CURRENT_VOLUME.key]
    change: float = quote[JsonTKN.CHANGE.key]

    alert_type: str = rule_result[JsonTKN.ALERT_TYPE.key]
    warning: bool = rule_result[JsonTKN.WARNING.key]
    suppress: bool = rule_result[JsonTKN.SUPPRESS_APNS.key]

    cfg = ALERT_TYPES.get(alert_type)
    if not cfg:
        return None

    cur = fmt(current)
    message = cfg[JsonTKN.MESSAGE.key](ticker, cur, rule_result)

    return {
        JsonTKN.TICKER.key: ticker,
        JsonTKN.ALERT_TYPE.key: alert_type,
        JsonTKN.QUOTE.key: round(current, 1),
        JsonTKN.VOLUME.key: volume,
        JsonTKN.MESSAGE.key: message,
        JsonTKN.WARNING.key: warning,
        JsonTKN.SUPPRESS_APNS.key: suppress,
        JsonTKN.CHANGE.key: change,
    }


def alert_priority(
    alert: Mapping[str, Any]
) -> int:
    kind: str = alert[JsonTKN.ALERT_TYPE.key]
    cfg = ALERT_TYPES.get(kind)
    return cfg[JsonTKN.PRIO.key] if cfg else 0


def evaluate_alert(
    quote: Mapping[str, Any],
) -> Optional[Mapping[str, Any]]:
    current: float = quote[JsonTKN.CURRENT_QUOTE.key]
    change: float = quote[JsonTKN.CHANGE.key]
    volume: int = quote[JsonTKN.CURRENT_VOLUME.key]
    avg_volume: int = quote[JsonTKN.AVERAGE_VOLUME.key]
    year_low: float = quote[JsonTKN.YEAR_LOW.key]
    last_alert_quote: float = quote[JsonTKN.LAST_ALERT_QUOTE.key]

    rules: List[Optional[Mapping[str, Any]]] = [
        volume_rule(current, volume, avg_volume, change),
        bottom_rule(current, year_low),
        rise_rule(current, last_alert_quote),
        fall_rule(current, last_alert_quote),
    ]

    alerts: List[Mapping[str, Any]] = [
        build_alert(quote, result)
        for result in rules
        if result
    ]

    if not alerts:
        return None

    alert: Mapping[str, Any] = max(alerts, key=alert_priority)
    alert[JsonTKN.SECTOR.key] = quote[JsonTKN.SECTOR.key]
    alert[JsonTKN.OPENING_QUOTE.key] = quote[JsonTKN.OPENING_QUOTE.key]
    return alert

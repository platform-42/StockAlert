from typing import (
    Optional,
    Dict,
    Any
)
from lib.core.tokens import JsonTKN


RuleResult = Dict[str, Any]


def volume_rule(
    current: float,
    volume: float,
    avg_volume: float,
    change: float,
    min_trade_value: float = 1_000_000
) -> Optional[RuleResult]:
    trade_value = volume * current
    if volume >= avg_volume * 1.5 and trade_value >= min_trade_value:
        return {
            JsonTKN.SUPPRESS_APNS.key: True,
            JsonTKN.ALERT_TYPE.key: "VOLUME",
            JsonTKN.TRADE_VALUE.key: trade_value,
            JsonTKN.WARNING.key: change < 0.0
        }
    return None


def bottom_rule(
    current: float,
    year_low: float
) -> Optional[RuleResult]:
    if current < year_low * 1.1:
        return {
            JsonTKN.SUPPRESS_APNS.key: True,
            JsonTKN.ALERT_TYPE.key: "BOTTOM",
            JsonTKN.REFERENCE.key: year_low,
            JsonTKN.WARNING.key: True
            }
    return None


def rise_rule(
    current: float,
    last_alert_quote: float
) -> Optional[RuleResult]:
    if current >= last_alert_quote * 1.05:
        return {
            JsonTKN.SUPPRESS_APNS.key: False,
            JsonTKN.ALERT_TYPE.key: "RISE",
            JsonTKN.REFERENCE.key: last_alert_quote,
            JsonTKN.WARNING.key: False
            }
    return None


def fall_rule(
    current: float,
    last_alert_quote: float
) -> Optional[RuleResult]:
    if current <= last_alert_quote * 0.95:
        return {
            JsonTKN.SUPPRESS_APNS.key: False,
            JsonTKN.ALERT_TYPE.key: "FALL",
            JsonTKN.REFERENCE.key: last_alert_quote,
            JsonTKN.WARNING.key: True
            }
    return None

from typing import (
    Any,
    Dict,
    Mapping
)
from datetime import (
    datetime,
    timezone
)
from lib.core.tokens import (
    JsonTKN,
    StocksCFG
)

#
#   quote selection predicate -> check existence quote for given day
#
def quote_select_predicate(
    ticker: str
) -> Dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    return {
        JsonTKN.TICKER.key: ticker,
        JsonTKN.DATE.key: today.isoformat(),
    }

#
#   quotes selection predicate -> all quotes for given sector and day
#
def quotes_select_predicate(
    sector: str
) -> Dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    return {
        JsonTKN.DATE.key: today.isoformat(),
        JsonTKN.SECTOR.key: sector.upper()
    }


def quote_insert_payload(
    date: str,
    stock: Mapping[str, Any],
    market: Mapping[str, float],
) -> Dict[str, Any]:
    now: datetime = datetime.now(timezone.utc)
    opening_quote: float = market[JsonTKN.OPENING_QUOTE.key]
    sector: str = stock[StocksCFG.SECTOR.key].strip().upper()
    payload: Dict[str, Any] = {
        JsonTKN.AVERAGE_VOLUME.key: market[JsonTKN.AVERAGE_VOLUME.key],
        JsonTKN.CREATED_AT.key: now,
        JsonTKN.CURRENT_QUOTE.key: market[JsonTKN.CURRENT_QUOTE.key],
        JsonTKN.CHANGE.key: market[JsonTKN.CHANGE.key],
        JsonTKN.CURRENT_VOLUME.key: market[JsonTKN.CURRENT_VOLUME.key],
        JsonTKN.DATE.key: date,
        JsonTKN.DESCRIPTION.key: stock[StocksCFG.DESCRIPTION.key],
        JsonTKN.LAST_ALERT_AT.key: None,
        JsonTKN.LAST_ALERT_QUOTE.key: opening_quote,
        JsonTKN.LAST_UPDATED_AT.key: now,
        JsonTKN.MOVING_AVERAGE_30.key: market[JsonTKN.MOVING_AVERAGE_30.key],
        JsonTKN.MOVING_AVERAGE_20.key: market[JsonTKN.MOVING_AVERAGE_20.key],
        JsonTKN.MOVING_AVERAGE_10.key: market[JsonTKN.MOVING_AVERAGE_10.key],
        JsonTKN.OPENING_QUOTE.key: opening_quote,
        JsonTKN.SECTOR.key: sector,
        JsonTKN.TICKER.key: stock[StocksCFG.TICKER.key],
        JsonTKN.YEAR_HIGH.key: market[JsonTKN.YEAR_HIGH.key],
        JsonTKN.YEAR_LOW.key: market[JsonTKN.YEAR_LOW.key],
        JsonTKN.DAYS_SINCE_YEAR_HIGH.key: market[JsonTKN.DAYS_SINCE_YEAR_HIGH.key]
    }
    if StocksCFG.BREAKOUT_QUOTE.key in stock:
        payload[JsonTKN.BREAKOUT_QUOTE.key] = stock[StocksCFG.BREAKOUT_QUOTE.key]
    if StocksCFG.COLLAPSE_QUOTE.key in stock:
        payload[JsonTKN.COLLAPSE_QUOTE.key] = stock[StocksCFG.COLLAPSE_QUOTE.key]
    return payload


def quote_update_payload(
    stock: Mapping[str, Any],
    market: Mapping[str, float],
) -> Dict[str, Dict[str, Any]]:
    now: datetime = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        JsonTKN.CURRENT_QUOTE.key: market[JsonTKN.CURRENT_QUOTE.key],
        JsonTKN.CHANGE.key: market[JsonTKN.CHANGE.key],
        JsonTKN.CURRENT_VOLUME.key: market[JsonTKN.CURRENT_VOLUME.key],
        JsonTKN.AVERAGE_VOLUME.key: market[JsonTKN.AVERAGE_VOLUME.key],
        JsonTKN.YEAR_HIGH.key: market[JsonTKN.YEAR_HIGH.key],
        JsonTKN.YEAR_LOW.key: market[JsonTKN.YEAR_LOW.key],
        JsonTKN.LAST_UPDATED_AT.key: now,
        JsonTKN.DAYS_SINCE_YEAR_HIGH.key: market[JsonTKN.DAYS_SINCE_YEAR_HIGH.key]
    }
    if JsonTKN.BREAKOUT_QUOTE.key in stock:
        payload[JsonTKN.BREAKOUT_QUOTE.key] = stock[JsonTKN.BREAKOUT_QUOTE.key]
    if JsonTKN.COLLAPSE_QUOTE.key in stock:
        payload[JsonTKN.COLLAPSE_QUOTE.key] = stock[JsonTKN.COLLAPSE_QUOTE.key]
    return {"$set": payload}


def quote_update_alert_state_payload(
    now: datetime,
    last_alert_quote: float
) -> Dict[str, Dict[str, Any]]:
    return {
        "$set": {
            JsonTKN.LAST_ALERT_AT.key: now,
            JsonTKN.LAST_ALERT_QUOTE.key: last_alert_quote
        }
    }

def quote_update_payload_after_alert(
    now: datetime,
    current_quote: float
) -> Dict[str, Dict[str, Any]]:
    return {
        "$set": {
            JsonTKN.LAST_ALERT_AT.key: now,
            JsonTKN.LAST_ALERT_QUOTE.key: current_quote,
            JsonTKN.LAST_UPDATED_AT.key: now,
        }
    }


#
#   alert payloads
#
def alert_insert_payload(
    alert: Mapping[str, Any],
) -> Dict[str, Any]:
    created_at: datetime = datetime.now(timezone.utc)
    payload: Dict[str, Any] = dict(alert)
    payload[JsonTKN.DATE.key] = created_at.date().isoformat()
    payload[JsonTKN.CREATED_AT.key] = created_at
    return payload

#
#   alert_select_predicate -> look if alert already exists
#
#       (date, ticker, alertType)
#
def alert_select_predicate(
    ticker: str,
    alert_type: str
) -> Dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    return {
        JsonTKN.DATE.key: today.isoformat(),
        JsonTKN.TICKER.key: ticker,
        JsonTKN.ALERT_TYPE.key: alert_type
    }

#
#   alerts select predicate -> select events for given day and priority
#
#       (sector, createdAt)
#
def alerts_select_predicate(
    sector: str
) -> Dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    created_at = datetime(today.year, today.month, today.day)
    return {
        JsonTKN.SECTOR.key: sector.upper(),
        JsonTKN.CREATED_AT.key: {
            "$gte": created_at
            }
        }

#
#   devices payload
#
def devices_select_predicate(
    device_id: str,
) -> Dict[str, Any]:
    return {
        JsonTKN.DEVICE_ID.key: device_id
    }


def devices_insert_payload(
    device_id: str,
    push_token: str,
) -> Dict[str, Any]:
    now: datetime = datetime.now(timezone.utc)
    return {
        JsonTKN.DEVICE_ID.key: device_id,
        JsonTKN.PUSH_TOKEN.key: push_token,
        JsonTKN.CREATED_AT.key: now,
        JsonTKN.LAST_UPDATED_AT.key: now
    }


def devices_update_payload(
    push_token: str,
) -> Dict[str, Any]:
    now: datetime = datetime.now(timezone.utc)
    return {
        "$set": {
            JsonTKN.PUSH_TOKEN.key: push_token,
            JsonTKN.LAST_UPDATED_AT.key: now
        }
    }

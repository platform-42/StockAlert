from typing import (
    Any,
    Dict,
    Tuple
)

import re

from lib.core.tokens import StocksCFG

TICKER_RE = re.compile(r'^[A-Z0-9\.]+$')


def validate_ticker(
    stock: Dict[str, Any]
) -> Tuple[bool, str]:
    ticker: str = stock.get(StocksCFG.TICKER.key)
    if not ticker:
        return False, "missing ticker"
    if ticker != ticker.upper():
        return False, "ticker not uppercase"
    if not TICKER_RE.match(ticker):
        return False, "invalid ticker format"
    return True, ""


def validate_sector(
    stock: Dict[str, Any]
) -> Tuple[bool, str]:
    sector: str = stock.get(StocksCFG.SECTOR.key)
    if not sector:
        return False, "missing sector"
    sector = sector.strip().upper()
    if sector not in ["AI", "3D", "QUANTUM"]:
        return False, "invalid sector"
    return True, ""


def validate_breakout(
    stock: Dict[str, Any]
) -> Tuple[bool, str]:
    if StocksCFG.BREAKOUT_QUOTE.key in stock:
        val = stock[StocksCFG.BREAKOUT_QUOTE.key]
        if not isinstance(val, (int, float)):
            return False, "breakoutQuote must be numeric"
        if val <= 0:
            return False, "breakoutQuote must be > 0"
    return True, ""


def validate_collapse(
    stock: Dict[str, Any]
) -> Tuple[bool, str]:
    if StocksCFG.COLLAPSE_QUOTE.key in stock:
        val = stock[StocksCFG.COLLAPSE_QUOTE.key]
        if not isinstance(val, (int, float)):
            return False, "collapseQuote must be numeric"
        if val <= 0:
            return False, "collapseQuote must be > 0"
    return True, ""


def validate_stock(
    stock: Dict[str, Any]
) -> Tuple[bool, str]:

    result, diagnostics = validate_ticker(stock)
    if not result:
        return result, diagnostics

    result, diagnostics = validate_sector(stock)
    if not result:
        return result, diagnostics

    result, diagnostics = validate_breakout(stock)
    if not result:
        return result, diagnostics

    result, diagnostics = validate_collapse(stock)
    if not result:
        return result, diagnostics

    return True, ""

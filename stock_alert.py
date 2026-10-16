#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Filename: stock_alert.py
    Author: Diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2026-02-05
    Version: 1.0.0
    Description: 
        Retrieve stock via yFinance package
        Send APNS alert
        Save stock tickers in Quote and Alert collection for iOS-app retrieval
"""
import argparse
import sys
import os
import time

from datetime import datetime

from ops_stats import OpsClient
from lib.core.args import (
    Argument
)
from lib.core.tokens import (
    JsonTKN,
    StocksCFG,
    MongoCFG,
)
from lib.core.ops import (
    ComponentType,
    ComponentName,
    Customer
)
from lib.core.utils import load_yaml
from lib.validation.validation import validate_stock
from lib.alerts.market import (
    fetch_market
)
from lib.mongo.persistence_factory import (
    init_db,
    init_indexes_quotes,
    init_indexes_alerts
)
from lib.alerts.alerts import evaluate_alert
from lib.alerts.apns_pyapns import send_apns_alert
from lib.mongo.persistence import (
    db_insert,
    db_select,
    db_select_all,
    db_update,
)
from lib.mongo.payloads import (
    quote_select_predicate,
    quote_insert_payload,
    quote_update_payload,
    quote_update_alert_state_payload,
    alert_insert_payload,
    alert_select_predicate
)

client = OpsClient(flush_interval_s=30)

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    client.update_state(
        Customer.PLATFORM42.key,
        ComponentType.CHANNEL.key,
        ComponentName.STOCKALERT.key,
        False
        )
    client.close()

sys.excepthook = handle_uncaught_exception


def main():
    parser = argparse.ArgumentParser(description="StockAlert Monitor")
    parser.add_argument(Argument.MONGODB.key, required=True, help="Path to mongodb.yml")
    parser.add_argument(Argument.STOCKS.key, required=True, help="Path to stocks.yml")
    parser.add_argument(Argument.APNS.key, required=True, help="Path to apns.yml")
    args = parser.parse_args()

    #
    #   load YAML config files from /etc/prod or /etc/aws
    #
    stocks_cfg = load_yaml(args.stocks)
    mongodb_cfg = load_yaml(args.mongodb)
    apns_cfg = load_yaml(args.apns)

    #
    #   confirm stock alert is up in dashboard
    #
    client.update_state(
        Customer.PLATFORM42.key,
        ComponentType.CHANNEL.key,
        ComponentName.STOCKALERT.key,
        True
        )


    #
    #   create Mongo connection and create unique indexes on Mongo collections
    #
    db = init_db(mongodb_cfg)
    init_indexes_quotes(db)
    init_indexes_alerts(db)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    #
    #   stock (LIST of tickers) -> YAML static data
    #   market (DICT - 1 ticker of YAHOO info) -> Dynamic YAHOO market data
    #   quote (DICT - 1 archived ticker quote for alert engine
    #   alert (DICT - alert event) -> all consolidated alerts mongo alerts collection
    #
    for stock in stocks_cfg[StocksCFG.STOCKS.key]:
        start_elapsed = time.perf_counter()
        is_valid, diagnostics = validate_stock(stock)
        if not is_valid:
            print(diagnostics)
            sys.exit(os.EX_CONFIG)
        ticker = stock[StocksCFG.TICKER.key]
        market = fetch_market(ticker)
        quote_predicate = quote_select_predicate(ticker)
        quote_projection = [
            JsonTKN.OPENING_QUOTE.key,
            JsonTKN.CURRENT_QUOTE.key,
            JsonTKN.CURRENT_VOLUME.key,
            JsonTKN.AVERAGE_VOLUME.key,
            JsonTKN.YEAR_LOW.key,
            JsonTKN.LAST_ALERT_AT.key,
            JsonTKN.CHANGE.key
        ]
        quote_doc = db_select(
            db[MongoCFG.COLLECTION_QUOTES.key],
            quote_predicate,
            quote_projection
        )
        if quote_doc is None:
            payload = quote_insert_payload(today, stock, market)
            db_insert(db[MongoCFG.COLLECTION_QUOTES.key], payload)
        else:
            payload = quote_update_payload(stock, market)
            db_update(db[MongoCFG.COLLECTION_QUOTES.key], quote_predicate, payload)
        quote_doc = db_select(
            db[MongoCFG.COLLECTION_QUOTES.key],
            quote_predicate
        )

        print(quote_doc)
        alert = evaluate_alert(quote_doc)
        if alert:
            #
            #   Log alert
            #
            alert_predicate = alert_select_predicate(
                alert[JsonTKN.TICKER.key],
                alert[JsonTKN.ALERT_TYPE.key]
            )
            alert_doc = db_select(
                db[MongoCFG.COLLECTION_ALERTS.key],
                alert_predicate
            )
            if alert_doc is None:
                alert_payload = alert_insert_payload(alert)
                db_insert(
                    db[MongoCFG.COLLECTION_ALERTS.key],
                    alert_payload
                )
            #
            #   Send APNS to all registered devices
            #
            device_predicate = {}
            device_projection = [
                JsonTKN.PUSH_TOKEN.key,
            ]
            device_tokens_docs = db_select_all(
                db[MongoCFG.COLLECTION_DEVICES.key],
                device_predicate,
                device_projection
            )
            for device_token_doc in device_tokens_docs:
                if not alert[JsonTKN.SUPPRESS_APNS.key]:
                    print(f"ALERT - {alert[JsonTKN.TICKER.key]}")
                    send_apns_alert(
                        apns_cfg,
                        alert,
                        device_token_doc[JsonTKN.PUSH_TOKEN.key]
                    )
            #
            #   update reporting timestamp to create suppress window
            #   rise and fall alerts work on delta, no suppress window needed
            #
            db_update(
                db[MongoCFG.COLLECTION_QUOTES.key],
                quote_predicate,
                quote_update_alert_state_payload(
                    datetime.utcnow(),
                    quote_doc[JsonTKN.CURRENT_QUOTE.key]
                )
            )
        stop_elapsed = time.perf_counter()
        client.update_stats(
            Customer.PLATFORM42.key,
            ComponentType.CHANNEL.key,
            ComponentName.STOCKALERT.key,
            1,
            0,
            (stop_elapsed - start_elapsed) * 1000
        )

if __name__ == "__main__":
    main()

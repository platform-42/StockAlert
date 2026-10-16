#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Filename: stock_api.py
    Author: Diederick de Buck (diederick.de.buck@platform-42.com)
    Date: 2026-02-05
    Version: 1.0.0
    Description: 
        RestAPI services for StockAlert
        Device API's for registering for push notifications
        Quote API's to retrieve quotes per sector
        Alert API's to retrieve alerts per sector
"""
import argparse
import time

from http import HTTPStatus
from flask import (
    Flask,
    request,
    jsonify
    )
from pydantic import (
    BaseModel,
    ValidationError
    )
from ops_stats import OpsClient
from lib.core.utils import (
    load_yaml
)
from lib.core.endpoints import (
    HttpEndpoints,
    QueryStringParam
)
from lib.core.tokens import (
    JsonTKN,
    MongoCFG,
    StockAPICFG,
    AppCFG
    )
from lib.core.args import (
    Argument
)
from lib.core.ops import (
    ComponentType,
    ComponentName,
    Customer
)
from lib.mongo.persistence_factory import (
    init_db,
    init_indexes_devices
    )
from lib.mongo.payloads import (
    devices_select_predicate,
    devices_insert_payload,
    devices_update_payload,
    quotes_select_predicate,
    alerts_select_predicate
    )
from lib.mongo.persistence import (
    db_select,
    db_select_all,
    db_insert,
    db_update,
    db_delete
    )

client = OpsClient(flush_interval_s=30)


class DeviceRegistration(BaseModel):
    deviceId: str
    pushToken: str


def create_app(
    mongo_cfg: dict,
    stockapi_cfg: dict
) -> Flask:
    app = Flask("StockAlert Devices Service")

    app.config[AppCFG.MONGO.key] = mongo_cfg
    app.config[AppCFG.STOCKAPI.key] = stockapi_cfg
    app.config[AppCFG.PERSISTENCE.key] = init_db(mongo_cfg)
    init_indexes_devices(app.config[AppCFG.PERSISTENCE.key])

    #
    #   For every request, check for valid API-key or reject
    #
    @app.before_request
    def check_api_key():
        key = request.headers.get("X-API-Key")
        stockapi_cfg = app.config[AppCFG.STOCKAPI.key]
        stockapi_root = stockapi_cfg[StockAPICFG.ROOT.key]
        #
        #   API key in HTTP header is always string
        #   so, we must enforce string casting on our YAML config spec of API key
        #
        if key != str(stockapi_root[StockAPICFG.API_KEY.key]):
            return jsonify({
                JsonTKN.STATUS.key: "error",
                JsonTKN.MESSAGE.key: "unauthorized"
                }), HTTPStatus.UNAUTHORIZED
        #
        #   The first valid request will set the service state to "running" in the OpsStats dashboard
        #
        client.update_state(
            Customer.PLATFORM42.key,
            ComponentType.FLASK.key,
            ComponentName.STOCKAPI.key,
            True
            )
        return None

    #
    #   Remove iOS device from receiving APNS-events
    #
    @app.route(HttpEndpoints.DEVICES_DEREGISTER.key, methods=["DELETE"])
    def device_deregister():
        try:
            payload = DeviceRegistration(**request.json)
        except ValidationError as e:
            return jsonify({
                JsonTKN.STATUS.key: "error",
                JsonTKN.MESSAGE.key: e.errors()
                }), HTTPStatus.BAD_REQUEST

        action = "deleted"
        devices = app.config[AppCFG.PERSISTENCE.key][MongoCFG.COLLECTION_DEVICES.key]
        devices_predicate = devices_select_predicate(payload.deviceId)
        device_doc = db_select(devices, devices_predicate)
        if device_doc:
            db_delete(devices, devices_predicate)
        return jsonify({
            JsonTKN.STATUS.key: "ok",
            JsonTKN.ACTION.key: action,
            JsonTKN.DEVICE_ID.key: payload.deviceId
        })

    #
    #   Register iOS device for receiving APNS-events
    #
    @app.route(HttpEndpoints.DEVICES_REGISTER.key, methods=["POST"])
    def device_register():
        try:
            payload = DeviceRegistration(**request.json)
        except ValidationError as e:
            return jsonify({
                JsonTKN.STATUS.key: "error",
                JsonTKN.MESSAGE.key: e.errors()
                }), HTTPStatus.BAD_REQUEST

        devices = app.config[AppCFG.PERSISTENCE.key][MongoCFG.COLLECTION_DEVICES.key]
        devices_predicate = devices_select_predicate(payload.deviceId)
        device_doc = db_select(devices, devices_predicate)

        if device_doc is None:
            insert_payload = devices_insert_payload(payload.deviceId, payload.pushToken)
            db_insert(devices, insert_payload)
            action = "inserted"
        else:
            update_payload = devices_update_payload(payload.pushToken)
            db_update(devices, devices_predicate, update_payload)
            action = "updated"

        return jsonify({
            JsonTKN.STATUS.key: "ok",
            JsonTKN.ACTION.key: action,
            JsonTKN.DEVICE_ID.key: payload.deviceId
        })

    #
    #   Get finance data per sector - 50, 30, 10 day moving averages included
    #
    @app.route(HttpEndpoints.QUOTES_BY_SECTOR.key, methods=["GET"])
    def quotes_sector():
        start_elapsed = time.perf_counter()
        quotes = app.config[AppCFG.PERSISTENCE.key][MongoCFG.COLLECTION_QUOTES.key]
        sector = request.args.get(QueryStringParam.SECTOR.key)
        if not sector:
            stop_elapsed = time.perf_counter()
            client.update_stats(
                Customer.PLATFORM42.key,
                ComponentType.FLASK.key,
                ComponentName.STOCKAPI.key,
                1,
                1,
                (stop_elapsed - start_elapsed) * 1000
            )
            return jsonify({
                JsonTKN.STATUS.key: "error",
                JsonTKN.MESSAGE.key: "Missing 'sector' query parameter"
                }), HTTPStatus.BAD_REQUEST

        quotes_predicate = quotes_select_predicate(sector)
        quotes_cursor = db_select_all(quotes, quotes_predicate)
        quotes_list = []
        for quotes_doc in quotes_cursor:
            quotes_doc.pop(JsonTKN.ID.key, None) # not serializable
            quotes_list.append(quotes_doc)
        stop_elapsed = time.perf_counter()
        client.update_stats(
            Customer.PLATFORM42.key,
            ComponentType.FLASK.key,
            ComponentName.STOCKAPI.key,
            1,
            0,
            (stop_elapsed - start_elapsed) * 1000
            )
        return jsonify({
            JsonTKN.STATUS.key: "ok",
            JsonTKN.COUNT.key: len(quotes_list),
            JsonTKN.SECTOR.key: sector,
            JsonTKN.QUOTES.key: quotes_list
        })

    #
    #   Get alerts per sector
    #
    @app.route(HttpEndpoints.ALERTS_BY_SECTOR.key, methods=["GET"])
    def alerts_prio():
        start_elapsed = time.perf_counter()
        alerts = app.config[AppCFG.PERSISTENCE.key][MongoCFG.COLLECTION_ALERTS.key]
        sector = request.args.get(QueryStringParam.SECTOR.key)
        if not sector:
            stop_elapsed = time.perf_counter()
            client.update_stats(
                Customer.PLATFORM42.key,
                ComponentType.FLASK.key,
                ComponentName.STOCKAPI.key,
                1,
                1,
                (stop_elapsed - start_elapsed) * 1000
            )
            return jsonify({
                JsonTKN.STATUS.key: "error",
                JsonTKN.MESSAGE.key: "Missing 'sector' query parameter"
                }), HTTPStatus.BAD_REQUEST

        alerts_predicate = alerts_select_predicate(sector)
        alerts_cursor = db_select_all(alerts, alerts_predicate)
        alerts_list = []
        for alerts_doc in alerts_cursor:
            alerts_doc.pop(JsonTKN.CREATED_AT, None) # not serializable
            alerts_doc.pop(JsonTKN.ID.key, None) # not serializable
            alerts_list.append(alerts_doc)
        stop_elapsed = time.perf_counter()
        client.update_stats(
            Customer.PLATFORM42.key,
            ComponentType.FLASK.key,
            ComponentName.STOCKAPI.key,
            1,
            0,
            (stop_elapsed - start_elapsed) * 1000
            )
        return jsonify({
            JsonTKN.STATUS.key: "ok",
            JsonTKN.COUNT.key: len(alerts_list),
            JsonTKN.ALERTS.key: alerts_list
        })

    return app


def main():
    parser = argparse.ArgumentParser(description="StockAPI webservice")
    parser.add_argument(Argument.MONGODB.key, required=True, help="Path to mongodb.yml")
    parser.add_argument(Argument.STOCK_API.key, required=True, help="Path to stock_api.yml")
    args = parser.parse_args()

    #
    #   Declare Flask app down before starting the webservice, so that OpsStats can report on the service state
    #
    client.update_state(
        Customer.PLATFORM42.key,
        ComponentType.FLASK.key,
        ComponentName.STOCKAPI.key,
        False
        )

    #
    #   load YAML config files from /etc/prod
    #
    mongodb_cfg = load_yaml(args.mongodb)
    stock_api_cfg = load_yaml(args.stock_api)
    stock_api_root = stock_api_cfg[StockAPICFG.ROOT.key]

    #
    #   create app instance for Flask
    #
    app = create_app(
        mongodb_cfg,
        stock_api_cfg
        )
    app.run(
        host=stock_api_root[StockAPICFG.HOST.key],
        port=stock_api_root[StockAPICFG.PORT.key]
    )

if __name__ == "__main__":
    main()

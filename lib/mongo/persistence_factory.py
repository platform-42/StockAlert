from typing import (
    Any,
    Dict,
    Mapping
)
from pymongo import MongoClient
from pymongo.collection import Collection
from lib.core.tokens import (
    JsonTKN,
    MongoCFG
)


def init_db(
    mongo_cfg: Mapping[str, Any]
) -> Dict[str, Collection]:
    mongo_root: Mapping[str, Any] = mongo_cfg[MongoCFG.ROOT.key]
    client: MongoClient = MongoClient(mongo_root[MongoCFG.URI.key])
    db = client[mongo_root[MongoCFG.DATABASE.key]]
    return {
        MongoCFG.COLLECTION_QUOTES.key: db[mongo_root[MongoCFG.COLLECTION_QUOTES.key]],
        MongoCFG.COLLECTION_ALERTS.key: db[mongo_root[MongoCFG.COLLECTION_ALERTS.key]],
        MongoCFG.COLLECTION_DEVICES.key: db[mongo_root[MongoCFG.COLLECTION_DEVICES.key]],
    }


def init_indexes_quotes(
    db: Mapping[str, Collection]
) -> None:
    quotes = db[MongoCFG.COLLECTION_QUOTES.key]
    quotes.create_index(
        [
            (JsonTKN.TICKER.key, 1),
            (JsonTKN.DATE.key, 1),
        ],
        unique=True
    )


def init_indexes_devices(
    db: Mapping[str, Collection]
) -> None:
    devices = db[MongoCFG.COLLECTION_DEVICES.key]
    devices.create_index(
        [
            (JsonTKN.DEVICE_ID.key, 1)
        ],
        unique=True
    )
    devices.create_index(
        [
            (JsonTKN.PUSH_TOKEN.key, 1)
        ],
        unique=True,
        sparse=True
    )


def init_indexes_alerts(
    db: Mapping[str, Collection]
) -> None:
    alerts = db[MongoCFG.COLLECTION_ALERTS.key]
    alerts.create_index([
        (JsonTKN.DATE.key, 1),
        (JsonTKN.TICKER.key, 1),
        (JsonTKN.ALERT_TYPE, 1)
        ],
        unique=True
    )

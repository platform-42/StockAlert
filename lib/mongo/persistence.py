from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Optional,
    List
)
from pymongo.collection import Collection


def db_select(
    collection: Collection,
    predicate: Mapping[str, Any],
    projection: Optional[Iterable[str]] = None,
) -> Optional[Dict[str, Any]]:
    proj = None
    if projection:
        proj = {field: 1 for field in projection}

    return collection.find_one(predicate, proj)


def db_select_all(
    collection: Collection,
    predicate: Optional[Mapping[str, Any]] = None,
    projection: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    if predicate is None:
        predicate = {}
    proj = None
    if projection:
        proj = {field: 1 for field in projection}

    return list(collection.find(predicate, proj))


def db_insert(
    collection: Collection,
    payload: Mapping[str, Any],
) -> None:
    collection.insert_one(dict(payload))


def db_update(
    collection: Collection,
    predicate: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> None:
    collection.update_one(predicate, payload)


def db_delete(
    collection: Collection,
    predicate: Mapping[str, Any]
) -> None:
    collection.delete_one(predicate)

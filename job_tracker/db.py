""""
DB concerns
"""

import json
from datetime import datetime
from typing import Any
from bson import ObjectId
import logging

from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection


logging.basicConfig(level=logging.INFO)


def mongo_collection(client, db: str, collection: str) -> Collection:
    """
    Wrapper returning a mongo collection
    :param client: mongo singleton class
    :param db:
    :param collection:
    :return: mongo collection
    """
    database = client[db]
    return database[collection]


class MongoDb:
    """
    Mongo DB singleton access to limit total connections via single object
    """
    _instance = None

    def __new__(cls, uri):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(uri)
        return cls._instance


class ManageDocs:
    """
    Upsert class to run upsert operation in mongodb
    """
    def __init__(self, client, db: str, collection: str):
        self.collection = mongo_collection(client, db, collection)

    @staticmethod
    def find_duplicates(collection, id_field):
        pipeline = [
            {
                "$sort": {
                    "fetched": DESCENDING
                }
            },
            {
                "$group": {
                    "_id": {f"{id_field}": f"${id_field}"},
                    "unique_ids": {"$addToSet": "$_id"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            },
            {
                "$project": {
                    "ids_to_delete": {"$slice": ["$unique_ids", 1, {"$size": "$unique_ids"}]}
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        return [ObjectId(d) for doc in results for d in doc["ids_to_delete"]]

    @staticmethod
    def delete_duplicates(collection, duplicate_refs: list):
        result = collection.delete_many({"_id": {"$in": duplicate_refs}})
        return result.deleted_count

    def deduplicate(self, documents: list, id_field: str) -> dict:
        results = self.collection.insert_many(documents)
        duplicates = self.find_duplicates(self.collection, id_field)
        inserted_document_ids = results.inserted_ids
        return {
            "inserted": len(inserted_document_ids),
            "updated": self.delete_duplicates(self.collection, duplicates),
            "results": parse_mongo(
                list(self.collection.find({"_id": {"$in": inserted_document_ids}}))
            )
        }


def parse_mongo(result):
    """
    Wrapper for MongoJSONEncoder

    :param result:
    :return: parsed results
    """
    return json.loads(MongoJSONEncoder().encode(result))


class MongoJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for ObjectId and date time fields in mongodb
    """
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

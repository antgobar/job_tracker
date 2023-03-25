""""
DB concerns
"""

import json
from datetime import datetime
from typing import Any
from bson import ObjectId

from pymongo import MongoClient
from pymongo.collection import Collection, UpdateOne

from job_tracker.config import Config


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

    def __new__(cls, uri=Config.MONGO_URI):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance = MongoClient(uri)
        return cls._instance


class UpsertDocs:
    """
    Upsert class to run upsert operation in mongodb
    """
    def __init__(self, client, db: str, collection: str):
        self.collection = mongo_collection(client, db, collection)

    def upsert(self, documents: list[dict], id_field: str):
        """
        Applies upsert on a list of documents and reference id values

        :param documents:
        :param id_field:
        :return: results of bulk write operation
        """
        ids = self.get_ids(documents, id_field)
        operations = self.upsert_operations(documents, ids, id_field)
        return self.collection_bulk_write(self.collection, operations)

    @staticmethod
    def get_ids(documents: list, id_field: str) -> list:
        """
        Extracts id fields from documents

        :param documents:
        :param id_field:
        :return: id values
        """
        return [doc[id_field] for doc in documents]

    @staticmethod
    def upsert_operations(documents: list[dict], ids: list[str], id_field) -> list:
        """
        Collates upsert operations into a single object

        :param documents:
        :param ids:
        :param id_field:
        :return: upsert operation list
        """
        return [
            UpdateOne({id_field: id_}, {"$set": new_doc}, upsert=True) for id_, new_doc in zip(ids, documents)
        ]

    @staticmethod
    def collection_bulk_write(collection: Collection, operations: list) -> dict:
        """
        Bulk write operation in mongodb

        :param collection:
        :param operations:
        :return: parsed results of bulk write operation
        """
        result = collection.bulk_write(operations)
        return parse_mongo(result.bulk_api_result)


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

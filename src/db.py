from pymongo import MongoClient, UpdateOne
from pymongo.collection import Collection, UpdateOne


def jobs_collection(uri: str, db: str, collection: str) -> Collection:
    client = MongoClient('mongodb://root:password@localhost:27017/')
    db = client["job_tracker"]
    return db["jobs"]


def get_ids(jobs: list, id_field: str) -> list:
    return [doc[id_field] for doc in jobs]


def upsert_operations(jobs: list[dict], ids_to_update: list[str]) -> list[UpdateOne]:
    return [
        UpdateOne({"ids": ids}, {"$set": new_doc}, upsert=True) for ids, new_doc in zip(ids_to_update, jobs)
    ]


def collection_bulk_write(collection, operations):
    result = collection.bulk_write(operations)
    return result.bulk_api_result

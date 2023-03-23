"""
API interface for job tracker applications
Two routes:
/update_jobs triggers the ETL pipeline and upserts moongodb and returns results on the upsert operation
/stored_jobs returns the jobs currently in mongodb
"""

from fastapi import FastAPI

from tracker import track_jobs
from db import mongo_collection, parse_mongo

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Tasman"}


@app.get("/update_jobs")
async def update_jobs(
        location: str | None = "Chicago, Illinois",
        key_word: str | None = "data engineering",
        min_pay: int | None = 100_000
):
    return track_jobs(location, key_word, min_pay)


@app.get("/stored_jobs")
async def stored_jobs():
    jobs_collection = mongo_collection("job_tracker", "jobs")
    return parse_mongo(list(jobs_collection.find()))

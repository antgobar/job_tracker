"""
API interface for job tracker applications
Two routes:
/update_jobs triggers the ETL pipeline and upserts moongodb and returns results on the upsert operation
/stored_jobs returns the jobs currently in mongodb
"""
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

from job_tracker.tracker import track_jobs
from job_tracker.db import MongoDb, mongo_collection, parse_mongo


app = FastAPI()
handler = Mangum(app)
client = MongoDb()


# logging.basicConfig(level=logging.INFO)
#
# results = track_jobs(client, "Chicago, Illinois", "data engineering", 100_000)
# logging.info(results)


@app.get("/")
async def root():
    return {
        "message": "Hello Tasman",

    }


@app.put("/update_jobs")
async def update_jobs(
        location: str | None = "Chicago, Illinois",
        keyword: str | None = "data engineering",
        min_pay: int | None = 100_000
):
    return track_jobs(client, location, keyword, min_pay)


@app.get("/stored_jobs")
async def stored_jobs():
    jobs_collection = mongo_collection(client, "job_tracker", "jobs")
    return {
        "total_jobs": jobs_collection.count_documents({}),
        "jobs": parse_mongo(list(jobs_collection.find()))
    }


@app.delete("/wipe")
async def wipe():
    jobs_collection = mongo_collection(client, "job_tracker", "jobs")
    result = jobs_collection.delete_many({})
    return JSONResponse({"deleted": result.deleted_count})


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0")

"""
API interface for job tracker applications
Two routes:
/update_jobs triggers the ETL pipeline and upserts moongodb and returns results on the upsert operation
/stored_jobs returns the jobs currently in mongodb
"""
import logging

from fastapi import FastAPI, HTTPException
from mangum import Mangum

from job_tracker.tracker import track_jobs
from job_tracker.db import MongoDb, mongo_collection, parse_mongo
from job_tracker.config import Config


description = """
JobTracker API helps you keep up to date with the latest
job adverts on the USAJob site. 

### How to:

* Call the **etl** endpoint with your desired 
parameters to fetch and update jobs already in the db

* Call the **jobs** endpoint to view all jobs fetched by this app

* Call the **wipe** endpoint to clear the db
"""


app = FastAPI(
    title="JobTrackerApp",
    description=description,
    version="0.1.0",
)


handler = Mangum(app)
client = MongoDb(Config.MONGO_URI)
jobs_collection = mongo_collection(client, "job_tracker", "jobs")


@app.get("/")
async def root():
    return {"message": "Hello Tasman"}


@app.put("/etl")
async def etl(
        location: str | None = "Chicago, Illinois",
        keyword: str | None = "data engineering",
        min_pay: int | None = 100_000
):
    try:
        return track_jobs(client, location, keyword, min_pay)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
async def jobs():

    try:
        return {
            "total_jobs": jobs_collection.count_documents({}),
            "jobs": parse_mongo(list(jobs_collection.find()))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/wipe")
async def wipe():
    result = jobs_collection.delete_many({})
    try:
        return {"deleted": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = track_jobs(client, "Chicago, Illinois", "data engineering", 100_000)
    logging.info(results)

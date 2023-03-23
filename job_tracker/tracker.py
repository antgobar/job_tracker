"""
Local interface for job tracker. Triggers job API calls and mongodb upsert operations
"""

from jobs import Jobs, USAJobApi
from db import UpsertDocs
from config import Config


def track_jobs(location: str, key_word: str, min_pay: int):
    """
    Main interface for job tracker

    :param location:
    :param key_word:
    :param min_pay:
    :return: query and database operation results
    """
    api = USAJobApi(
        base_url="https://data.usajobs.gov/api/search",
        api_user=Config.API_USER,
        api_key=Config.API_KEY
    )
    jobs = Jobs(
        api=api, location=location, key_word=key_word, min_pay=min_pay
    )

    jobs_data = jobs.job_data()
    job_count = len(jobs_data)

    if job_count == 0:
        return {"query_job_count": 0, "results": None}

    upserter = UpsertDocs("job_tracker", "jobs")

    return {
        "query_job_count": job_count,
        "results": upserter.upsert(jobs_data, "job_id")
    }


if __name__ == "__main__":
    Config.MONGO_URI = "mongodb://root:password@localhost:27017/"

    results = track_jobs(
        location="Chicago, Illinois",
        key_word="data engineering",
        min_pay=10000
    )
    print(results)

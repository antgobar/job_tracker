"""
Local interface for job tracker. Triggers job API calls and mongodb upsert operations
"""
import logging

from job_tracker.jobs import Jobs, USAJobApi
from job_tracker.db import UpsertDocs
from job_tracker.config import Config


logging.basicConfig(level=logging.INFO)


def track_jobs(db_client, location: str, keyword: str, min_pay: int):
    """
    Main interface for job tracker
    :param db_client: database client e.g. mongo
    :param location:
    :param keyword:
    :param min_pay:
    :return: query and database operation results
    """
    api = USAJobApi(
        base_url="https://data.usajobs.gov/api/search",
        api_user=Config.API_USER,
        api_key=Config.API_KEY
    )
    jobs = Jobs(
        api=api, location=location, keyword=keyword, min_pay=min_pay
    )

    jobs_data = jobs.job_data()
    job_count = len(jobs_data)

    if job_count == 0:
        return {"query_job_count": 0, "results": None}

    upserter = UpsertDocs(db_client, "job_tracker", "jobs")

    return {
        "query_job_count": job_count,
        "results": upserter.upsert(jobs_data, "job_id")
    }

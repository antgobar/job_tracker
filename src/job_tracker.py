import os

from env import env
from api import USAJobApi
from jobs import Jobs


if __name__ == "__main__":
    LOCATION = "Chicago, Illinois"
    ROLE = "Data Engineer"
    ROLE_KEY_WORD = "data engineering"

    api = USAJobApi(
        base_url=os.getenv("API_BASE_URL"),
        api_user=os.getenv("API_USER"),
        api_key=os.getenv("API_KEY")
    )
    jobs = Jobs(api=api, location=LOCATION, role=ROLE, key_word=ROLE_KEY_WORD)
    data = jobs.job_data()

    jobs_collection = mongo_collection(
        os.getenv("MONGO_CONNECTION"), "job_tracker", "jobs"
    )

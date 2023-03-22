import os
from datetime import datetime
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv


load_dotenv()


LOCATION = "Chicago, Illinois"
ROLE = "Data Engineer"
ROLE_KEY_WORD = "data engineering"


class JobApi(ABC):

    @abstractmethod
    def search_jobs(self, *args, **kwargs):
        raise NotImplementedError


class USAJobApi(JobApi):
    def __init__(self, base_url: str, host: str, api_user: str, api_key: str) -> None:
        self.base_url = base_url
        self.host = host
        self.headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": api_user,
            "Authorization-Key": api_key
        }

    def search_jobs(self, location: str, role: str, key_word: str):
        params = {
            "keyword": key_word,
            "LocationName": location,
            "PositionTitle": role
        }

        response = requests.get(self.base_url, headers=self.headers, params=params)
        return response.json()["SearchResult"]["SearchResultItems"]

    @staticmethod
    def _parse_remuneration(remuneration_field):
        return [remuneration_field["MinimumRange"], remuneration_field["MaximumRange"]]

    @staticmethod
    def _parse_locations(location_field, searched_location):
        return [
            location["LocationName"] for location in location_field if searched_location in location["LocationName"]
        ]

    @staticmethod
    def _parse_duration(start_date: str, end_date: str) -> tuple:
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f")
        end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f")
        month_diff = (end.year - start.year) * 12
        total_month_diff = month_diff + end.month - start.month
        return total_month_diff, end.day - start.day

    @staticmethod
    def _parse_dates(full_datetime) -> str:
        return full_datetime.split("T")[0]

    def job_data(self, location: str, job_info: dict):
        duration_months, duration_days = self._parse_duration(
            job_info["PositionStartDate"],
            job_info["PositionEndDate"]
        )

        return {
            "job_id": job_info["MatchedObjectId"],
            "position": job_info["PositionTitle"],
            "locations": self._parse_locations(job_info["PositionLocation"], location),
            "oragnisation": job_info["OrganizationName"],
            "department": job_info["DepartmentName"],
            "grade": job_info["JobGrade"][0]["Code"],
            "renumeration_range": self._parse_remuneration(job_info["PositionRemuneration"][0]),
            "start_date": job_info["PositionStartDate"].split("T")[0],
            "duration_months": duration_months,
            "duration_days": duration_days,
            "close_date": job_info["ApplicationCloseDate"].split("T")[0],
            "link": job_info["PositionURI"]
        }


class Jobs:
    def __init__(self, api: JobApi, location: str, key_word: str, role: str = None) -> None:
        self.api = api
        self.location = location
        self.key_word = key_word
        self.role = role
        if role is None:
            self.role = key_word

    def _find_jobs(self):
        return self.api.search_jobs(self.location, self.key_word, self.role)

    def job_data(self, nest_key: str = None):
        for job in self._find_jobs():
            yield job[nest_key] if nest_key else job

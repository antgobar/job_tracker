import logging
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass

import requests


logging.basicConfig(level=logging.INFO)


class JobApi(ABC):
    @abstractmethod
    def search_jobs(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class JobData:
    job_id: str
    position: str
    locations: list
    organisation: str
    department: str
    grade: str
    remuneration_range: tuple
    start_date: str
    duration_months: str
    duration_days: str
    close_date: str
    link: str


class USAJobApi(JobApi):
    def __init__(self, base_url: str, api_user: str, api_key: str) -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": api_user,
            "Authorization-Key": api_key
        }

    def search_jobs(self, location: str, role: str, key_word: str):
        params = {
            "keyword": key_word,
            "LocationName": location,
            "PositionTitle": role
        }
        logging.info(f"Query with params: {params}")
        response = requests.get(self.base_url, headers=self.headers, params=params)
        logging.info(f"Response: {response.status_code}")
        return response.json()["SearchResult"]["SearchResultItems"]

    @staticmethod
    def _parse_remuneration(remuneration_field):
        return remuneration_field["MinimumRange"], remuneration_field["MaximumRange"]

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

    def job_details(self, job: dict, location: str):
        job_info = job["MatchedObjectDescriptor"]
        duration_months, duration_days = self._parse_duration(
            job_info["PositionStartDate"],
            job_info["PositionEndDate"]
        )

        return JobData(
            job["MatchedObjectId"],
            job_info["PositionTitle"],
            self._parse_locations(job_info["PositionLocation"], location),
            job_info["OrganizationName"],
            job_info["DepartmentName"],
            job_info["JobGrade"][0]["Code"],
            self._parse_remuneration(job_info["PositionRemuneration"][0]),
            job_info["PositionStartDate"].split("T")[0],
            duration_months,
            duration_days,
            job_info["ApplicationCloseDate"].split("T")[0],
            job_info["PositionURI"]
        )

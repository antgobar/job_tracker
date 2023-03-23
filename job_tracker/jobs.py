"""
Interface with jobs API and Extraction and Transformations of ETL
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass

import requests


logging.basicConfig(level=logging.INFO)


class JobApi(ABC):
    """
    Job API abstract class defining required methods
    Useful for implementing API clients from other job API providers
    """
    @abstractmethod
    def search_jobs(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def job_details(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class JobData:
    """
    Dataclass defining record schema
    """
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
    """
    API client for USAJob API
    Includes various parser methods for required fields
    """
    def __init__(self, base_url: str, api_user: str, api_key: str) -> None:
        self.base_url = base_url
        self.headers = {
            "User-Agent": api_user,
            "Authorization-Key": api_key
        }

    def search_jobs(self, location: str, role: str, key_word: str, min_pay: int, max_pay: int) -> list:
        """
        API caller passing in various parameters to the http request
        :param location:
        :param role:
        :param key_word:
        :param min_pay:
        :param max_pay:
        :return:
        """
        params = {
            "keyword": key_word,
            "LocationName": location,
            "PositionTitle": role,
            "RemunerationMinimumAmount": min_pay,
            "RemunerationMaximumAmount": max_pay,
            "ResultsPerPage": 500  # max results per page
        }
        logging.info(f"Query with params: {params}")

        response = requests.get(self.base_url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise ConnectionError(f"Could not connect to API: {self.base_url}")

        logging.info(f"Response: {response.status_code}")
        return response.json()["SearchResult"]["SearchResultItems"]

    @staticmethod
    def _parse_remuneration(remuneration_field: dict) -> tuple:
        return remuneration_field["MinimumRange"], remuneration_field["MaximumRange"]

    @staticmethod
    def _parse_locations(location_field, searched_location):
        return set(
            [location["LocationName"] for location in location_field if searched_location in location["LocationName"]]
        )

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
        """
        Creates JobData objects from job responses using JobData schema
        :param job:
        :param location:
        :return: structured record
        """
        job_info = job["MatchedObjectDescriptor"]
        duration_months, duration_days = self._parse_duration(
            job_info["PositionStartDate"],
            job_info["PositionEndDate"]
        )

        return JobData(
            job["MatchedObjectId"],
            job_info["PositionTitle"],
            list(self._parse_locations(job_info["PositionLocation"], location)),
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


class Jobs:
    """
    Main interface for Job API caller
    """
    def __init__(
            self,
            api: JobApi,
            location: str = None,
            key_word: str = None,
            role: str = None,
            min_pay: int = None,
            max_pay: int = None
    ) -> None:
        self.api = api
        self.location = location
        self.key_word = key_word
        self.role = role
        self.min_pay = min_pay
        self.max_pay = max_pay

    def _find_jobs(self):
        return self.api.search_jobs(
            self.location, self.key_word, self.role, self.min_pay, self.max_pay
        )

    def job_data(self):
        return [
            self.api.job_details(job, self.location).__dict__ for job in self._find_jobs()
        ]

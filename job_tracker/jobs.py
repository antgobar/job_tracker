"""
Interface with jobs API and Extraction and Transformations of ETL
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

import requests

from job_tracker.models import JobData


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


class USAJobApi(JobApi):
    """
    API client for USAJob API
    Includes various parser methods for required fields
    """
    def __init__(self, base_url: str, api_user: str, api_key: str) -> None:
        self.base_url = base_url
        self._headers = {
            "User-Agent": api_user,
            "Authorization-Key": api_key
        }

    def search_jobs(self, location: str, role: str, keyword: str, min_pay: int, max_pay: int) -> list:
        """
        API caller passing in various parameters to the http request
        :param location:
        :param role:
        :param keyword:
        :param min_pay:
        :param max_pay:
        :return:
        """
        params = {
            "keyword": keyword,
            "LocationName": location,
            "PositionTitle": role,
            "RemunerationMinimumAmount": min_pay,
            "RemunerationMaximumAmount": max_pay,
            "ResultsPerPage": 500  # max results per page
        }
        logging.info(f"Query with params: {params}")

        response = requests.get(self.base_url, headers=self._headers, params=params)
        if response.status_code != 200:
            raise ConnectionError(f"Could not connect to API: {self.base_url}")

        response.raise_for_status()
        return response.json()["SearchResult"]["SearchResultItems"]

    @staticmethod
    def _parse_remuneration(remuneration_field: dict) -> dict:
        return {
            "min": remuneration_field["MinimumRange"],
            "max": remuneration_field["MaximumRange"]
        }

    @staticmethod
    def _parse_locations(location_field, searched_location):
        return set(
            [location["LocationName"] for location in location_field if searched_location in location["LocationName"]]
        )

    def _parse_duration(self, start_date: str, end_date: str) -> int:
        start = datetime.strptime(self._parse_dates(start_date), "%Y-%m-%d")
        end = datetime.strptime(self._parse_dates(end_date), "%Y-%m-%d")
        difference = end - start
        return difference.days

    @staticmethod
    def _parse_dates(full_datetime: str) -> str:
        return full_datetime.split("T")[0]

    def job_details(self, job: dict, location: str):
        """
        Creates JobData objects from job responses using JobData schema
        :param job:
        :param location:
        :return: structured record
        """
        job = job["MatchedObjectDescriptor"]
        return JobData(
            job["PositionID"],
            job["PositionTitle"],
            list(self._parse_locations(job["PositionLocation"], location)),
            job["OrganizationName"],
            job["DepartmentName"],
            job["JobGrade"][0]["Code"],
            self._parse_remuneration(job["PositionRemuneration"][0]),
            self._parse_dates(job["PositionStartDate"]),
            self._parse_duration(job["PositionStartDate"], job["PositionEndDate"]),
            self._parse_dates(job["ApplicationCloseDate"]),
            job["PositionURI"]
        )


class Jobs:
    """
    Main interface for Job API caller
    """
    def __init__(
            self,
            api: JobApi,
            location: str = None,
            keyword: str = None,
            role: str = None,
            min_pay: int = None,
            max_pay: int = None
    ) -> None:
        self.api = api
        self.location = location
        self.keyword = keyword
        self.role = role
        self.min_pay = min_pay
        self.max_pay = max_pay

    def _find_jobs(self):
        return self.api.search_jobs(
            location=self.location,
            keyword=self.keyword,
            role=self.role,
            min_pay=self.min_pay,
            max_pay=self.max_pay
        )

    def job_data(self):
        return [
            self.api.job_details(job, self.location).__dict__ for job in self._find_jobs()
        ]

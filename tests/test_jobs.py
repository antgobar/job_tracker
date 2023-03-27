from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest

from job_tracker.jobs import USAJobApi, Jobs, JobApi
from job_tracker.models import JobData


@pytest.fixture
def test_api_instance():
    return USAJobApi("url", "user", "key")


class TestUSAJobApi:
    def test_constructor(self, test_api_instance):
        assert test_api_instance.base_url == "url"
        assert test_api_instance._headers == {"User-Agent": "user", "Authorization-Key": "key"}

    @patch("job_tracker.jobs.requests.get")
    def test_search_jobs(self, mock_requests_get, test_api_instance):
        mock_requests_get_instance = MagicMock()
        mock_requests_get_instance.status_code = 200
        mock_requests_get_instance.json = lambda: {"SearchResult": {"SearchResultItems": "result_items"}}
        mock_requests_get_instance.raise_for_status = lambda: None
        mock_requests_get.return_value = mock_requests_get_instance

        assert test_api_instance.search_jobs("location", "role", "key_word", 1, 10) == "result_items"

        mock_requests_get.assert_called_with(
            "url",
            headers={"User-Agent": "user", "Authorization-Key": "key"},
            params={
                "keyword": "key_word",
                "LocationName": "location",
                "PositionTitle": "role",
                "RemunerationMinimumAmount": 1,
                "RemunerationMaximumAmount": 10,
                "ResultsPerPage": 500
            }
        )

    @patch("job_tracker.jobs.requests.get")
    def test_search_jobs_raises(self, mock_requests_get, test_api_instance):
        mock_requests_get_instance = MagicMock()
        mock_requests_get_instance.status_code = 400
        mock_requests_get.return_value = mock_requests_get_instance

        with pytest.raises(ConnectionError) as err:
            test_api_instance.search_jobs("location", "role", "key_word", 1, 10)

        assert "Could not connect to API: url" in str(err)

    def test_parse_parse_remuneration(self, test_api_instance):
        assert test_api_instance._parse_remuneration(
            {"MinimumRange": 1, "MaximumRange": 10}
        ) == {"min": 1, "max": 10}

    def test_parse_locations(self, test_api_instance):
        test_data = (
            [{"LocationName": "London"}, {"LocationName": "Leeds"}, {"LocationName": "Leeds"}],
            "Leeds"
        )

        assert test_api_instance._parse_locations(*test_data) == {"Leeds"}

    def test_parse_duration(self, test_api_instance):
        assert test_api_instance._parse_duration("2023-01-01", "2023-01-04") == 3

    def test_parse_dates(self, test_api_instance):
        assert test_api_instance._parse_dates("2023-01-01T12345") == "2023-01-01"

    @patch("job_tracker.jobs.datetime")
    @patch("job_tracker.jobs.USAJobApi._parse_duration")
    def test_job_details(self, mock_duration, mock_datetime, test_api_instance):
        mock_duration.return_value = 3
        mock_datetime.now.return_value = datetime(2023, 1, 4)
        test_job = {
            "MatchedObjectDescriptor": {
                "PositionID": "id",
                "PositionTitle": "title",
                "PositionLocation": [{"LocationName": "Leeds"}],
                "OrganizationName": "org",
                "DepartmentName": "dept",
                "JobGrade": [{"Code": "ABC"}],
                "PositionRemuneration": [{"MinimumRange": 1, "MaximumRange": 10}],
                "PositionStartDate": "2023-01-01T1234",
                "PositionEndDate": "2023-01-04T1234",
                "ApplicationCloseDate": "2023-01-02T1234",
                "PositionURI": "abc123"
            }
        }

        actual = test_api_instance.job_details(test_job, "Leeds")

        assert actual == JobData(
            "id",
            "title",
            ["Leeds"],
            "org",
            "dept",
            "ABC",
            {"min": 1, "max": 10},
            "2023-01-01",
            3,
            "2023-01-02",
            "abc123",
            datetime(2023, 1, 4)
        )


@pytest.fixture
def mock_job_api():
    return MagicMock(JobApi)


@pytest.fixture
def jobs_instance(mock_job_api):
    return Jobs(mock_job_api, "location", "keyword", "role", 1, 10)


class TestJobs:
    def test_constructor(self, jobs_instance, mock_job_api):
        assert jobs_instance.api == mock_job_api
        assert jobs_instance.location == "location"
        assert jobs_instance.keyword == "keyword"
        assert jobs_instance.role == "role"
        assert jobs_instance.min_pay == 1
        assert jobs_instance.max_pay == 10

    def test_find_jobs(self, jobs_instance, mock_job_api):
        mock_job_api.search_jobs.return_value = "jobs_found"

        assert jobs_instance._find_jobs() == "jobs_found"
        mock_job_api.search_jobs.assert_called_with(
            location="location",
            keyword="keyword",
            role="role",
            min_pay=1,
            max_pay=10
        )

    @patch("job_tracker.jobs.Jobs._find_jobs")
    def test_job_data(self, mock_find_jobs, jobs_instance, mock_job_api):

        class MockDict:
            ...

        mock_job_api.job_details.return_value = MockDict()
        mock_find_jobs.return_value = [1, 2, 3]

        assert jobs_instance.job_data() == [{}, {}, {}]
        mock_job_api.job_details.assert_called_with(3, "location")

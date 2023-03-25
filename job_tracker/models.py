from dataclasses import dataclass


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
    remuneration_range: dict
    start_date: str
    duration_days: int
    close_date: str
    link: str

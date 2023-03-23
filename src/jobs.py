from api import JobApi


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

    def job_data(self):
        return [
            self.api.job_details(job, self.location) for job in self._find_jobs()
        ]

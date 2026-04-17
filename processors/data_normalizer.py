from job import Job
from utils import datetime_generator

class DataNormalizer:
    """
    Normalize data from web search APIs and flatten their data structure
    """

    def __init__(self, serp_results, exa_results):
        self.serp_data = serp_results
        self.exa_data = exa_results

    def normalize_job_data(self):
        """
        Normalize SerpAPI search result data into Job data schema
        """

        jobs = []
        current_time = datetime_generator.generate_current_datetime()

        for item in self.serp_data + self.exa_data:
            job = Job(
                title=item.get("title", None),
                url=item.get("link", None),
                text=item.get("text", None), #SerpAPI doesn't return text(Job Description) so it requires to web-scrape later on
                searched_via=item.get("searched_via", None),
                date=current_time
            )

            jobs.append(job)

        print("Data conversion completed")
        print(f"Total jobs collected: {len(jobs)} jobs")
        return jobs


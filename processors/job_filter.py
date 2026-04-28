from typing import List
from job import Job
from urllib.parse import urlparse


class JobFilter:
    """
    Internal logic to filter out job data before passing it to the LLM job evaluator
    """
    EXCLUDING_DOMAINS = [
        "linkedin.com", "indeed.com", "ziprecruiter.com", "glassdoor.com", "huggingface.co",
        "github.com", "facebook.com", "wellfound.com", "jobs.weekday.works",
        "medium.com", "reddit.com"
    ]
    EXCLUDING_URL_SLUG = ["blog", "news", "article", "insights", "press", "media", "comments"]
    EXCLUDING_WORDS = ["senior", "head", "lead", "principal", "director", "manager"]
    SITES_For_BROWSER_AUTOMATION = ["workable.com"] # Problematic sites for web-scrapping; needed to pass to the LLM auto-browsing logic to handle

    def __init__(self, jobs):
        self.jobs = jobs


    def filter_jobs(self) -> List[Job]:
        """
        Filter out data that should be excluded in order to reduce the workload of Web scraping and LLM Evaluator (Save costs and improve latency)
        """

        filtered_jobs = []

        seen_urls = set()

        for job in self.jobs:

            path = urlparse(job.url).path.lower()
            path_parts = [p for p in path.split("/") if p] # just in case path contains an empty string ""

            # Skip duplicate URLs
            if job.url.lower() in seen_urls:
                continue
            seen_urls.add(job.url.lower())

            # First filter out URLs that unlikely offer global/worldwide remote roles, including general job board platforms, blogs, news etc
            if not any(domain in job.url.lower() for domain in self.EXCLUDING_DOMAINS):

                # Filter any urls that contains a slug like "blog" etc
                if not any(slug in path_parts for slug in self.EXCLUDING_URL_SLUG):

                    # Additionally, filter out data that contains these words on its title
                    if not any(word in job.title.lower() for word in self.EXCLUDING_WORDS):

                        # Pre-assign low_quality judgment before the web-scraping process
                        if any(word in job.url.lower() for word in self.SITES_For_BROWSER_AUTOMATION):
                            job.low_quality = True

                        filtered_jobs.append(job)

        return filtered_jobs

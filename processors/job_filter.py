from typing import List
from job import Job


class JobFilter:
    """
    Internal logic to filter out job data before passing it to the LLM job evaluator
    """
    EXCLUDING_SITES = ["linkedin.com", "indeed.com", "ziprecruiter.com", "glassdoor.com", "huggingface.co"]
    EXCLUDING_WORDS = ["senior", "head", "lead", "principal", "director", "manager"]
    AUTO_BROWSING_SITES = ["workable.com"] # Problematic sites for web-scrapping; needed to pass to the LLM auto-browsing logic to handle

    def __init__(self, jobs):
        self.jobs = jobs


    def filter_jobs(self) -> List[Job]:
        """
        Filter out data that should be excluded in order to reduce the workload of LLM Evaluator (Save costs and improve latency)
        """

        filtered_jobs = []

        seen_urls = set()

        for job in self.jobs:

            # Skip duplicate URLs
            if job.url in seen_urls:
                continue
            seen_urls.add(job.url)

            # First filter out URLs that point to these general job platforms that unlikely offer global/worldwide remote roles
            if not any(domain in job.url.lower() for domain in self.EXCLUDING_SITES):

                # Additionally, filter out data that contains these words on its title
                if not any(word in job.title.lower() for word in self.EXCLUDING_WORDS):

                    # Pre-assign low_quality judgment before the web-scraping process
                    if any(word in job.url.lower() for word in self.AUTO_BROWSING_SITES):
                        job.low_quality = True

                    filtered_jobs.append(job)

        return filtered_jobs
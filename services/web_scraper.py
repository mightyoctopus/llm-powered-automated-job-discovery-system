from typing import List
import requests
import time
import random
from job import Job
from bs4 import BeautifulSoup
from utils.request_controller import apply_delay

class WebScraper:
    """
    Web-scrape job description for job objects without description data (job.text = None)
    """

    def __init__(self, jobs):
        self.filtered_jobs = jobs


    def web_scrape(self) -> List[Job]:

        scrapped_jobs = []
        prev_domain = ""

        for i, job in enumerate(self.filtered_jobs):
            if not job.text:

                # Time sleep & update prev_domain for the next iteration
                prev_domain = apply_delay(index=i, job=job, prev_job_domain=prev_domain)

                try:
                    response = requests.get(job.url, timeout=12) # to be safe for slow responses sometimes

                    if response.status_code != 200:
                        print(f"JOB ID {i + 1}: Failed with status {response.status_code}\nURL: {job.url}")
                    else:
                        soup = BeautifulSoup(response.text, "lxml")
                        text = soup.get_text(separator="\n\n", strip=True)

                        if text:
                            # Assign the scraped text into the text attribute of Job object
                            job.text = text

                except requests.exceptions.RequestException as e:
                    print(f"JOB ID {i + 1}: Failed to scrape - {e}")



            scrapped_jobs.append(job)

        return scrapped_jobs
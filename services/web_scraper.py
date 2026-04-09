from typing import List
import requests
import time
import random
from job import Job
from bs4 import BeautifulSoup

class WebScraper:
    """
    Web-scrape job description for job objects without description data (job.text = None)
    """

    def __init__(self, jobs):
        self.filtered_jobs = jobs


    def web_scrape(self) -> List[Job]:

        scrapped_jobs = []
        for i, job in enumerate(self.filtered_jobs):
            if not job.text:
                try:
                    response = requests.get(job.url, timeout=12)

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

                # Small random delay (always)
                time.sleep(random.uniform(1, 2))

                # Batch pause (longer delay) every 15 jobs
                if (i + 1) % 15 == 0:
                    time.sleep(random.uniform(2, 5))

            scrapped_jobs.append(job)

        return scrapped_jobs
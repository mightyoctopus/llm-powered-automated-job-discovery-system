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
        error_pages = [] # Collect all 404, 410 or request error urls so it can separate them from the group of scrapped urls
        prev_domain = ""

        for i, job in enumerate(self.filtered_jobs):
            if not job.text:

                # Time sleep (conditional delay based on each case) & update prev_domain for the next iteration
                prev_domain = apply_delay(index=i, job=job, prev_job_domain=prev_domain)

                try:
                    print(f"Job {i} is being scrapped...")

                    # HEAD requests first (initial check for 404 or bad http responses)
                    try:
                        head_response = requests.head(
                            job.url,
                            allow_redirects=True,
                            timeout=5
                        )

                        # Drop immediately if 404, or 410 found
                        if head_response.status_code in [404, 410]:
                            print(f"JOB ID {i + 1}: Dropped (dead link {head_response.status_code})\nURL: {job.url}")
                            error_pages.append(job)
                            continue

                    except requests.exceptions.RequestException:
                        print(f"JOB ID {i + 1}: HEAD failed")

                    ### GET request starts from here ###
                    response = requests.get(job.url, timeout=12) # to be safe for slow responses sometimes

                    if response.status_code != 200:
                        print(f"JOB ID {i + 1}: Failed with status {response.status_code}\nURL: {job.url}")
                        scrapped_jobs.append(job) # jobs might fail to be scraped due to 500 or 403(bot blocking) so include this for now for further web scraping with browser automation later on
                    else:
                        soup = BeautifulSoup(response.text, "lxml")
                        text = soup.get_text(separator="\n\n", strip=True)

                        if text:
                            # Assign the scraped text into the text attribute of Job object
                            job.text = text

                        scrapped_jobs.append(job)

                except requests.exceptions.RequestException as e:
                    print(f"JOB ID {i + 1}: Failed to scrape - {e}")
                    scrapped_jobs.append(job)


        return scrapped_jobs
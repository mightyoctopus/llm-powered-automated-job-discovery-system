from typing import List
from urllib.parse import urlparse
import random
from job import Job


def no_adjacent_same_domains(jobs: List[Job], max_attempts=50):
    """
    Shuffle jobs to avoid jobs with adjacent domains straight to each other which can cause a throttling with bursty requests to domains (for web-scraping)
    :param jobs: a list of jobs
    :param max_attempts: maximum limit of domain shuffling
    :return: job list with a shuffled order of root domains
    """
    def get_root_domain(url):
        return urlparse(url).netloc

    for _ in range(max_attempts):
        random.shuffle(jobs)
        valid = True

        for i in range(len(jobs) - 1):
            if get_root_domain(jobs[i].url) == get_root_domain(jobs[i + 1].url):
                valid = False
                break

        if valid:
            return jobs

    return jobs
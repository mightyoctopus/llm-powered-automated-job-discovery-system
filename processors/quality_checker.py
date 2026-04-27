from typing import List
from job import Job

class QualityChecker:
    """
    Check if the job description of each job object has proper JD text
    """

    def __init__(self, jobs: List[Job]):
        self.jobs = jobs

    def check_jd_quality(self) -> List[Job]:
        """
        Check if job.text (job description) is at low quality which implies an improper web scrape or poor content.
        If determined as poor content, the Job objects (with low_quality=True) should pass to the auto-browsing class later on.
        """

        # Missing job related keywords
        keywords = [
            "responsibilities", "requirements", "experience",
            "qualifications", "skills", "what you'll do", "about the role"
        ]
        counter = 0
        for job in self.jobs:

            text = job.text or ""
            words = text.split()
            low_quality = False

            if job.searched_via == "exa":
                if len(words) < 80:
                    low_quality = True
            else:
                if len(words) < 150:
                    low_quality = True

            if not any(k in text.lower() for k in keywords):
                low_quality = True

            job.low_quality = low_quality

            if job.low_quality:
                counter += 1

        print(f"LOW QUALITY URLs: {counter} out of {len(self.jobs)} URLs")

        return self.jobs
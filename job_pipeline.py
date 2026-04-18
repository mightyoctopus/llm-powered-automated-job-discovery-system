import os
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv
import serpapi
from exa_py import Exa
import asyncio

from job import Job
from llm_modules.query_generator import QueryGenerator
from services.search_service import SearchService
from processors.data_normalizer import DataNormalizer
from processors.job_filter import JobFilter
from services.web_scraper import WebScraper
from processors.quality_checker import QualityChecker
from utils.request_controller import no_adjacent_same_domains
from services.browser_automation import BrowserAutomation
from llm_modules.job_evaluator import JobEvaluator
from services.export_service import ExportService

class JobPipeline:
    """
    Orchestrate the main workflow of LLM llm_modules and functions for the job discovery automation
    """

    load_dotenv()
    SERP_API_KEY = os.getenv("SERP_API_KEY")
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    JOB_SHEET_KEY = os.getenv("JOB_SHEET_KEY")

    def __init__(self, num_queries=3):
        self.num_queries = num_queries

    async def run(self):
        """
        The main workflow of the app.
        """

        ###========== Search Query Generator Agent Flow ==========###
        print("The main program started running")
        query_agent = QueryGenerator(num_queries=self.num_queries)

        queries = query_agent.get_queries()
        serp_queries = queries["serp"]
        exa_queries = queries["exa"]


        ###========== Web Search APIs Flow ==========###
        if not self.SERP_API_KEY:
            raise ValueError("SerpAPI API key not found in the environment variables")
        if not self.EXA_API_KEY:
            raise ValueError("Exa API key not found in the environment variables")

        serpapi_client = serpapi.Client(api_key=self.SERP_API_KEY)
        print("SerpAPI has been loaded!")
        exa_client = Exa(api_key=self.EXA_API_KEY)
        print("Exa has been loaded!")

        web_search_service = SearchService(serpapi_client, exa_client, serp_queries, exa_queries)
        print("Web Search is starting...")
        serp_search_results, exa_search_results = web_search_service.run_web_search()


        ###========== Data Normalizer ==========###
        data_normalizer = DataNormalizer(serp_search_results, exa_search_results)
        # all jobs that were finished being normalized
        total_jobs = data_normalizer.normalize_job_data()


        ###========== Job Filter ==========###
        job_filter = JobFilter(total_jobs)
        filtered_jobs = job_filter.filter_jobs()
        print(f"Job has been pre-filtered\nResult: {len(filtered_jobs)} Jobs Remaining")


        ### ========== Web Scraper ==========###
        # Shuffle domains and avoid adjacent domain ordering before web-scraping
        shuffled_jobs = no_adjacent_same_domains(filtered_jobs)

        web_scraper = WebScraper(shuffled_jobs)
        print("Job scraping is in process...")
        scraped_jobs = web_scraper.web_scrape()
        print(f"NUM OF SCRAPED JOBS: {len(scraped_jobs)}")


        ###========== Quality Checker ==========###
        quality_checker = QualityChecker(scraped_jobs)
        # mark low_quality = True for jobs with low-quality job description
        marked_jobs = quality_checker.check_jd_quality()
        print("Quality check on job descriptions are complete")

        ###========== Decision Routes ==========###
        valid_jobs = [job for job in marked_jobs if not job.low_quality] # low_quality = False
        invalid_jobs = [job for job in marked_jobs if job.low_quality]

        shuffled_invalid_jobs: List[Job] = no_adjacent_same_domains(invalid_jobs)

        # send invalid jobs to browser automation to enhance the job description quality by browsing scraping
        browser_automation = BrowserAutomation(shuffled_invalid_jobs)
        recovered_jobs = await browser_automation.run()

        # Combine all jobs before passing it to LLM Evaluator
        all_processed_jobs = valid_jobs + recovered_jobs

        # Filter jobs out further to pass them to the final evaluator:
        final_input_jobs = [job for job in all_processed_jobs if job.text and len(job.text.split()) > 150]


        ###========== LLM Evaluator ==========###
        job_evaluator = JobEvaluator(final_input_jobs)
        final_job_results: List[Job] = await job_evaluator.run_job_evaluations()

        print("FINAL RESULTS: ", final_job_results)


        ###========== Sorting Valid Jobs ==========###
        valid_final_jobs = [job for job in final_job_results if job.keep]
        manual_check_list = [job for job in final_job_results if job.manual_check_required]


        ###========== Export to Spreadsheet ==========###
        exporter = ExportService(self.JOB_SHEET_KEY, valid_final_jobs, manual_check_list)
        exporter.export_jobs()

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import serpapi
from exa_py import Exa

from llm_modules.query_generator import QueryGenerator
from services.search_service import SearchService
from processors.data_normalizer import DataNormalizer
from processors.job_filter import JobFilter
from services.web_scraper import WebScraper
from processors.quality_checker import QualityChecker

class JobPipeline:
    """
    Orchestrate the main workflow of LLM llm_modules and functions for the job discovery automation
    """

    load_dotenv()
    SERP_API_KEY = os.getenv("SERP_API_KEY")
    EXA_API_KEY = os.getenv("EXA_API_KEY")

    def run(self):
        """
        The main workflow of the app.
        """

        ###========== Search Query Generator Agent Flow ==========###
        print("The main program started running")

        client = OpenAI()
        print(f"OpenAI model was loaded successfully: {client}")

        query_agent = QueryGenerator(client)
        serp_queries, exa_queries = query_agent.get_queries()

        print(f"SERP Len: {len(serp_queries)} | Queries: {serp_queries}")
        print(f"EXA len: {len(exa_queries)} | Queries: {exa_queries}")


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

        print("SERP SEARCH RESULTS: ", serp_search_results)
        print("EXA SEARCH RESULTS: ", exa_search_results)


        ###========== Data Normalizer ==========###
        data_normalizer = DataNormalizer(serp_search_results, exa_search_results)
        # all jobs that were finished being normalized
        total_jobs = data_normalizer.normalize_job_data()
        print("TOTAL JOBS: ", len(total_jobs))


        ###========== Job Filter ==========###
        job_filter = JobFilter(total_jobs)
        filtered_jobs = job_filter.filter_jobs()
        print(f"Job has been pre-filtered\nResult: {len(filtered_jobs)} Jobs Remaining")
        print(filtered_jobs)


        ### ========== Web Scraper ==========###
        web_scraper = WebScraper(filtered_jobs)
        print("Job scraping is in process...")
        scrapped_jobs = web_scraper.web_scrape()
        print(f"NUM OF SCRAPPED JOBS: {len(scrapped_jobs)}")
        print("SCRAPPED JOBS: ", scrapped_jobs)


        ###========== Quality Checker ==========###
        quality_checker = QualityChecker(scrapped_jobs)
        # mark low_quality = True for jobs with low-quality job description
        marked_jobs = quality_checker.check_jd_quality()
        print("Quality check on job descriptions are complete")

        ###========== Decision Routes ==========###
        valid_jobs = [job for job in marked_jobs if not job.low_quality] # low_quality = False
        invalid_jobs = [job for job in marked_jobs if job.low_quality]

        recovered_jobs = ["run_browser_automation(invalid_jobs)"] # Implement later

        processed_jobs = valid_jobs + recovered_jobs



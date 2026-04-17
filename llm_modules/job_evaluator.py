from job import Job
from typing import List, Tuple, Dict, Any
import json
from openai import AsyncOpenAI
import openai
import asyncio

class JobEvaluator:
    """
    Evaluates Job objects as the final evaluating/filtering layer, selecting the most relevant jobs.
    """

    def __init__(self, jobs: List[Job], model="gpt-5.4", concurrency=3):
        self.client = AsyncOpenAI()
        self.jobs = jobs
        system_msg, base_user_msg = self.build_base_prompts()
        self.system_msg = system_msg
        self.base_user_msg = base_user_msg
        self.final_results = []
        self.model = model
        self.sem = asyncio.Semaphore(concurrency)


    def build_base_prompts(self) -> Tuple[str, str]:

        system_message = """
            You are a job evaluator that analyses text based on the provided job details and description of each job.
            Your major responsibility is to filter out any Job objects that contains irrelevant text and pick out only the actual job posts(openings) BEST tailored to my desired job types.
        """.strip()

        base_user_prompt = """
            You should filter out irrelevant jobs and only pick out the best jobs that fit these conditions:

            - They must be an AI engineer jobs (LLM Engineering, RAG, AI Agents, Agentic Systems, LoRA/QLoRA, Machine Learning or any jobs relevant in AI engineering). Otherwise keep=False.
            - they MUST be remote roles that are available for the global/worldwide regions, Asia, or South Korea. Otherwise keep=False.

            1. IMPORTANT REMOTE RULES:

            - The job MUST be accessible to a candidate residing in South Korea.

            - Accept if:
              - Remote worldwide / global / work from anywhere (with no specific regional restriction)
              - Remote APAC / Asia (explicitly includes multiple countries, not a single country)
              - Remote with no location restriction

            - Reject ONLY if:
              - Remote limited to a single country (e.g., "India Remote", "US Remote", "EU Remote only")
              - Remote limited to regions that exclude South Korea
              - Visa/work authorization restriction is clearly stated

            Examples:
            - "Remote - India only" → keep = False
            - "Remote - US only" → keep = False
            - "Remote - APAC" → keep = True
            - "Remote - Worldwide" → keep = True
            - "Remote Portugal" → keep = False


            2. EDGE CASE – REMOTE JOB BOARDS:

            - If the job is sourced from a known REMOTE JOB BOARD by its url (e.g., Working Nomads, WeWorkRemotely, Remote OK):

              → Do NOT treat the listed country/city as a strict work location.
              → It often represents the company’s location, not a hiring restriction.

            - In this case:
              - Ignore the stated location
              - Analyze the full job description for actual remote constraints

            - If there is NO explicit country restriction:
              → set manual_check_required = True

            - If NO location mentioned or unclear:
              → set keep = True

            - If you are confused:
              → set manual_check_required = True


            3. OTHER RULES:
            - Reject jobs that are not clearly AI engineering roles
            - Reject non-job pages like blog posts, listings, forums, Github repos etc
            - If the job description text is missing or extremely insufficient text length, mark manual_check_required = True and keep=False
            - Also, if the job is confusing or unclear for the remote work availability for South Korea, BUT it might be possible to be available for the region, then mark manual_check_required = True and keep=False 


            4. TIMEZONE / WORK HOURS MATCH RULES:

            - If the required timezone or work time overlap matches Asia or South Korea → keep = True
            - If timezone overlap is reasonably manageable and the role appears practically workable from South Korea, set keep = True. There's a high chance for Korea then!
            - If overlap is difficult but still possible for South Korea(remote) → keep = True


            Return ONLY valid JSON in this format without any comments or explanation:

            {
                "keep": boolean (keep = True if the job is available worldwide/global, or Asia/APAC, or South Korea),
                "score": int (0 to 100),
                "reason": string (short text within 150 characters), 
                "is_ai_role": boolean,
                "manual_check_required": boolean
            }
        """.strip()

        return system_message, base_user_prompt


    async def assess_job(self, index, job: Job):
        """
        Evaluates jobs by LLM and assign the final Job attributes based on the LLM's determination
        """

        async with self.sem:

            dynamic_user_prompt = self.base_user_msg + f"""
            Now, evaluate the following Job:

            Title: {job.title}
            URL: {job.url}
            Text: {job.text}

            """.strip()

            try:
                print(f"Job {index + 1} is being analyzed...")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_msg},
                        {"role": "user", "content": dynamic_user_prompt}
                    ]
                )

                try:
                    parsed_res: Dict[str, Any] = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    print(f"Invalid JSON at job {index}")
                    job.keep = False
                    job.manual_check_required = True
                    job.reason = "Invalid JSON response"
                    return job

                # Update objects in Job schema
                job.is_ai_role = parsed_res["is_ai_role"]
                job.keep = parsed_res["keep"]
                job.manual_check_required = parsed_res['manual_check_required']
                job.reason = parsed_res['reason']
                job.score = parsed_res['score']

                if not job.text or len(job.text.split()) <= 150:
                    job.keep = False
                    job.manual_check_required = True
                    job.reason = "Insufficient job description text"

                return job

            except openai.BadRequestError as e:
                print(f"Bad request: {e}")
                job.keep = False
                job.manual_check_required = True
                job.reason = "Evaluation failed due to a bad request error"
                return job
            except openai.APIError as e:
                print(f"General OpenAI error: {e}")
                job.keep = False
                job.manual_check_required = True
                job.reason = "Evaluation failed due to an API error"
                return job
            except Exception as e:
                print(f"Error calling LLM via OpenAI API: {e}")
                job.keep = False
                job.manual_check_required = True
                job.reason = "Evaluation failed due to a technical error"
                return job


    # Gather method
    async def run_job_evaluations(self):
        # list of coroutine functions
        tasks = [self.assess_job(i, job) for i, job in enumerate(self.jobs)]
        results = await asyncio.gather(*tasks)

        # Remove failed ones
        self.final_results = [result for result in results if result is not None]

        print("Job Evaluation is finished!")
        return self.final_results


    def run(self):
        return asyncio.run(self.run_job_evaluations())
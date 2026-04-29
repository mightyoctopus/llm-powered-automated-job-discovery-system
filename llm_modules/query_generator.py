from typing import List, Tuple, Dict
import json
from openai import OpenAI


class QueryGenerator:
    """
    Generate search operators and semantic search queries for web search APIs
    """

    system_message = """
                You specialize in crafting best and most efficient google search operators that work well.
                The prompt you generate will be used as queries for Exa and SerpAPI web search later on.
            """.strip()

    def __init__(self, num_queries):
        self.client = OpenAI()
        self.num_queries = num_queries
        self._queries = None # to use cached queries as best as possible (to avoid duplicate LLM calls)

    def build_serpapi_user_prompt(self) -> str:
        return f"""
                Generate {self.num_queries} Google search queries for job discovery.
            
                Goal:
                Find remote AI/LLM engineering roles (NOT data science heavy role) focused on:
                AI agents, agentic systems, RAG, LangChain, LangGraph, LoRA/QLoRA, AI integration, applied ML, LLM engineer, or backend with LLM integration role.
            
                Requirements:
                - Roles must be remote and available globally or in Asia/APAC (including South Korea).
                - Prefer junior to mid-level roles (avoid lead/senior-heavy roles unless realistic for ~3 - 5 years experience).
                - Target company ATS pages only (e.g., boards.greenhouse.io, jobs.lever.co, ashbyhq.com, workable.com, breezy.hr, smartrecruiters.com or anything that is similar or works great!).
                - Avoid general job boards (LinkedIn, Indeed, ZipRecruiter, etc.).
            
                STRICT QUERY FORMAT:
                Each query MUST follow this exact structure:
            
                site:<ATS_DOMAIN> ("<ROLE_OR_SKILL_1>" OR "<ROLE_OR_SKILL_2>" ... up to 6)
                ("<REMOTE_REGION_1>" OR "<REMOTE_REGION_2>" ... up to 6)
                -(<EXCLUDED_1> OR <EXCLUDED_2> ... up to 6)
                
                For example:
                site:boards.greenhouse.io ("AI engineer" OR "LLM" OR "RAG" OR "LangChain" OR "LangGraph" OR "agent") ("APAC" OR "Asia" OR "global" OR "worldwide" OR "timezone overlap") -(lead OR head OR staff OR principal OR director OR 'data scientist') 
                
            
                Rules:
                - Group 1: role/skill keywords (max 6)
                - Group 2: remote/location keywords (max 6)
                - Group 3: exclusion keywords (max 6)
                - Exclude terms like: lead, head, staff, principal, director, data scientist
                - Use realistic variations and diversity across queries
            
                Output:
                Return ONLY a JSON array of strings:
            
                [
                  "... exactly {self.num_queries} queries ..."
                ]
            
                Format Rules:
                - No markdown
                - No explanation
                - Valid JSON only
                - Exactly {self.num_queries} items
        """.strip()

    def build_exa_user_prompt(self) -> str:
        """
        Build a dynamic user message for Exa semantic search queries
        """

        return f"""
                Generate semantic search queries for my job search.

                Requirements:
                - I am looking for remote AI engineering roles focused on agentic systems, AI agents, RAG pipelines, LoRA/QLoRA fine-tuning, AI integration, AI-driven applications, and LLM engineering, AI/ML engineering or applied ML roles (BUT NOT DATA SCIENCE ROLES).
                - The role MUST be remote and available globally, worldwide, or in regions including ASIA/APAC (including South Korea).
                - Junior, mid-level, internship are preferred. Senior roles are acceptable if realistic for a ~3-year-experience developer.

                - Queries should be written in natural, human-like language optimized for semantic search (NOT heavy Google operator style).

                - Include strong job-intent signals in natural form:
                  (e.g. "hiring", "job opening", "career opportunity", "looking for", "open role")

               - Avoid irrelevant content such as blogs, articles, tutorials, forums, and news:
                  Instead of using negative phrases, prioritize strong positive job-intent signals like:
                  "hiring", "job opening", "open role", "career opportunity", "we are hiring"

                - IMPORTANT: Do NOT over-constrain queries.
                  Keep each query simple and realistic (3–4 core ideas).
                  Spread variations across multiple queries instead of stacking conditions.

                - Prioritize recall over strict filtering:
                  queries should help discover jobs that are harder to find via traditional search.

                - Output exactly this JSON schema:

                [
                    "... exactly {self.num_queries} strings ..."
                ]


                Format Rules:
                - Return only raw JSON.
                - No markdown fences.
                - No explanation.
                - The list must contain exactly {self.num_queries} strings.
                """.strip()


    def generate_queries_by_llm(self, user_msg):
        """
        Invoke OpenAI and generate LLM responses
        :arg user_msg: user message builder, either for Serp or Exa
        :return: raw search operator queries in JSON
        """

        try:
            print("LLM is generating the best search queries...")
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": user_msg}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM call for generating queries failed: {e}")



    def process_response(self) -> Dict[str, List[str]]:
        """
        load the LLM JSON response and separate each key (ser, exa) for easier process on SerpAPI and Exa individually.
        """

        try:
            llm_res_for_serp = self.generate_queries_by_llm(self.build_serpapi_user_prompt())
            serp_queries = json.loads(llm_res_for_serp)

            if not isinstance(serp_queries, list):
                raise ValueError("Serp queries must be in a list")

            if not all(isinstance(serp_query, str) for serp_query in serp_queries):
                raise ValueError("Serp queries must be strings")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM JSON response for SerpAPI: {e}\n")

        try:
            llm_res_for_exa = self.generate_queries_by_llm(self.build_exa_user_prompt())
            exa_queries = json.loads(llm_res_for_exa)

            if not isinstance(exa_queries, list):
                raise ValueError("Exa queries must be in a list")

            if not all(isinstance(exa_query, str) for exa_query in exa_queries):
                raise ValueError("Exa queries must be strings")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM JSON response for Exa: {e}\n")

        if len(serp_queries) != self.num_queries or len(exa_queries) != self.num_queries:
            raise ValueError(
                f"Expected exactly {self.num_queries} serp and {self.num_queries} exa queries, got serp={len(serp_queries)}, exa={len(exa_queries)}."
            )

        return {
            "serp": serp_queries,
            "exa": exa_queries
        }


    # Cache result and avoid calling LLM repeatedly
    def get_queries(self):
        """
        Use case: serp, exa = query_agent.get_queries()
        """
        if self._queries is None:
            self._queries = self.process_response()

        return self._queries


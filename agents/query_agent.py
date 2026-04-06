from typing import List, Tuple
import json


class QueryAgent:
    """
    Generate search operators and semantic search queries for web search APIs
    """

    system_message = """
                You specialize in crafting best and most efficient google search operators that work well.
                The prompt you generate will be used as queries for Exa and SerpAPI web search later on.
            """.strip()

    def __init__(self, openai, num_queries: int = 3):
        self.client = openai
        self.num_queries = num_queries
        self._queries = None # to use cached queries as best as possible (to avoid duplicate LLM calls)


    def build_user_prompt(self) -> str:
        """
        Build a dynamic user message to feed the LLM
        """

        # Ask the LLM to generate response in JSON
        return f"""
                Generate search queries for my job search.

                Requirements:
                - I need a remote AI engineering role focused on agentic systems, AI agents, RAG pipelines, LoRA/QLoRA fine-tuning, AI integration, AI-driven applications, and LLM engineering including frontier and open-source Hugging Face models.
                - The role must be remote-friendly for applicants from the global or worldwide region or ASIA, APAC or any upper category that includes South Korea. (Generate most used queries as possible that can include Asia region)
                - Junior, mid-level, internship are preferred. Senior roles are still acceptable if realistic for a 3-year-experience developer.
                - First {self.num_queries} queries must be formatted for the google search operator style for SERP queries, and the next {self.num_queries} queries are semantic search queries for Exa query style 
                - It must not target specific job boards like LinkedIn, Indeed etc. It must be queries that search for companies' direct hiring page or ATS including GreenHouse, Lever, Workable or anything that tends to have static HTML for easy web scraping with BS4 
                - Output exactly this JSON schema:

                {{
                  "serp": ["... exactly {self.num_queries} strings ..."],
                  "exa": ["... exactly {self.num_queries} strings ..."]
                }}

                Rules:
                - Return only raw JSON.
                - No markdown fences.
                - No explanation.
                - Each list must contain exactly {self.num_queries} strings.
                """.strip()


    def call_llm(self):
        """
        Invoke OpenAI and generate LLM responses
        :return: raw search operator queries
        """

        try:
            print("LLM is generating a response...")
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": self.build_user_prompt()}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")


    def process_response(self) -> Tuple[List[str], List[str]]:
        """
        load the LLM JSON response and separate each key (ser, exa) for easier process on SerpAPI and Exa individually.
        """

        try:
            llm_res = self.call_llm()
            data = json.loads(llm_res)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM JSON response: {e}\n")

        serp = data.get("serp")
        exa = data.get("exa")

        if not isinstance(serp, list) or not isinstance(exa, list):
            raise ValueError(f"Response must contain 'serp' and 'exa' as lists.\nRaw response: {llm_res}")

        if len(serp) != 10 or len(exa) != 10:
            raise ValueError(
                f"Expected exactly 10 serp and 10 exa queries, got serp={len(serp)}, exa={len(exa)}."
            )

        return serp, exa


    # Cache result and avoid calling LLM duplicate
    def get_queries(self):
        """
        Use case: serp, exa = query_agent.get_queries()
        """
        if self._queries is None:
            self._queries = self.process_response()

        return self._queries


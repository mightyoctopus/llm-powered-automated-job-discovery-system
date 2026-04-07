import time

class SearchService:
    """
    Provide web search tools via SerpAPI and Exa API for fetching job results on the internet
    """

    def __init__(self, serp_client, exa_client, serp_queries, exa_queries):
        self.serp_client = serp_client
        self.exa_client = exa_client
        self.serp_queries = serp_queries
        self.exa_queries = exa_queries


    def serpapi_web_search(self):
        """
        Search on the major search engines using SerpAPI for the SERPs data from Google, Bing, Yahoo, etc.
        """

        all_results = []
        for i, q in enumerate(self.serp_queries):
            try:
                response = self.serp_client.search({
                    "engine": "google",
                    "google_domain": "google.com",
                    "hl": "en",
                    "q": q
                })

                all_results.extend([
                    {**item, "searched_via": "serp"}
                    for item in response.get("organic_results", [])
                ])
                print(f"SerpAPI Search Iteration {i + 1} Finished")
                time.sleep(1)
            except Exception as e:
                print(f"[SerpAPI ERROR] Search Iteration {i + 1} failed: {e}")
                continue

        return all_results


    def exa_web_search(self):
        """
        Perform semantic web search using an Exa API for embedding-based retrieval over its own indexed web corpus.

        - semantically relevant content
        - long-tail or niche pages
        - results not easily surfaced via strict keyword search
        """
        all_exa_results = []

        for i, q in enumerate(self.exa_queries):
            try:
                response = self.exa_client.search(
                    query=q,
                    type="auto",
                    contents={"highlights": {"max_characters": 4000}},
                    exclude_domains=["linkedin.com", "indeed.com"],
                    exclude_text=["senior"] #Exclude all results that contain text of senior
                )
                print(f"Exa Search Iteration {i + 1} Finished")

                all_exa_results.extend([
                    {
                        "title": result.title,
                        "link": result.url,
                        "text": result.highlights[0] if result.highlights else None,
                        "searched_via": "exa"
                    }
                    for result in response.results
                ])
                time.sleep(1)
            except Exception as e:
                print(f"[Exa ERROR] Search Iteration {i + 1} failed: {e}")
                continue

        return all_exa_results


    def run_web_search(self):
        """
        Run all API modules together
        """
        serp_search_results = self.serpapi_web_search()
        exa_search_results = self.exa_web_search()
        print(f"Web search has been finished\nSerp: {len(serp_search_results)}\nExa: {len(exa_search_results)}")

        return serp_search_results, exa_search_results


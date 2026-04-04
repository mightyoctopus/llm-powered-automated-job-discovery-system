
class SearchService:
    """
    Provide web search tools via SerpAPI and Exa API for fetching job results on the internet
    """

    def __init__(self, serp, exa):
        self.serp_client = serp
        self.exa_client = exa


    def serpapi_web_search(self):
        """
        Search on the major search engines using SerpAPI for the SERPs data from Google, Bing, Yahoo, etc.
        """
        pass


    def exa_web_search(self):
        """
        Perform semantic web search using an Exa API for embedding-based retrieval over its own indexed web corpus.

        - semantically relevant content
        - long-tail or niche pages
        - results not easily surfaced via strict keyword search
        """
        pass

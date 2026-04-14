from typing import List
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
from bs4.element import Tag
import time
import random
from job import Job


class BrowserAutomation:
    """
    A fallback web-scraping service used after the initial web-scraping. This handles cases
    where basic HTTP scraping fails, especially for JS rendered pages and dynamic DOM content
    """

    def __init__(self, failed_jobs: List[Job], headless=False):
        self.failed_jobs: List[Job] = failed_jobs
        self.headless: bool = headless


    async def _init_browser(self):
        """
        Internal private method that configures PlayWright initialization
        """
        print("Browser Automation is starting...")
        p = await async_playwright().start()
        await asyncio.sleep(random.randint(1, 3))

        browser = await p.chromium.launch(headless=self.headless)
        page = await browser.new_page()

        return p, browser, page


    async def run(self) -> List[Job]:
        """
        Execute browser automation for failed jobs
        """

        p, browser, page = await self._init_browser()

        try:
            for failed_job in self.failed_jobs:
                await page.goto(failed_job.url, timeout=30000)
                # Wait for JS rendering and dynamic DOM to load
                await page.wait_for_load_state("networkidle")

                html = await page.content()

                if html:
                    soup = BeautifulSoup(html, "lxml")
                    footer = soup.find("footer")

                    # Remove footer
                    if footer:
                        footer.decompose()

                    # Remove junk tags
                    for tag in soup.find_all(["nav", "aside"]):
                        tag.decompose()


                    ### Remove the other messy HTML elements by classes and IDs
                    ### Commented this out because this filters out all content sometimes

                    # keywords = ["footer", "cookie", "privacy", "nav", "menu", "header"]
                    # for tag in list(soup.find_all(True)):

                    #     if not isinstance(tag, Tag) or tag.attrs is None:
                    #         continue

                    #     classes = " ".join(tag.get("class", []))
                    #     id_ = tag.get("id", "")

                    #     combined = f"{classes} {id_}".lower()

                    #     if any(keyword in combined for keyword in keywords):
                    #         tag.decompose()

                    text = soup.get_text(separator="\n\n", strip=True)
                    if text:
                        failed_job.text = text

                await asyncio.sleep(random.randint(3, 8))

        finally:
            await browser.close()
            await p.stop()

        print("Failed Job (JD) recovery has been finished!")
        return self.failed_jobs








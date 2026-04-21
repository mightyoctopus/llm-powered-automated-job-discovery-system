
---
# Automated Job Discovery System (LLM-Powered)

An **LLM-powered job discovery pipeline** that automates the process of finding, filtering, evaluating, and organizing high-quality AI/LLM job opportunities.

The system is designed to reduce repetitive manual job searching by combining structured pipeline logic with LLM-based reasoning at key decision points.

This system was originally built for my personal use to find remote AI engineering roles that are available for South Korea and relevant to what I am building. However, the overall design is flexible and can be extended into a more robust system supporting a wider range of job search criteria and use cases in the future.

---

## Overview

DEMO VIDEO: https://drive.google.com/file/d/1Vl3OONpfAYiVYzdSJE9nN-MDNDZKNqyQ/view?usp=sharing

Finding relevant AI jobs often involves:

* scanning multiple job boards
* opening and reviewing low-quality listings
* revisiting the same sources repeatedly
* manually tracking useful opportunities

This project addresses that by turning job discovery into a **repeatable, automated workflow**.

Instead of manually searching, the system:

* generates targeted search queries
* collects job listings from multiple sources
* filters and processes results
* evaluates relevance using an LLM
* outputs structured results for review

---

## Workflow

The system follows a structured pipeline:
![LLM Job Discovery Automation (2).jpg](assets/LLM%20Job%20Discovery%20Automation%20%282%29.jpg)

Each stage has a clearly defined responsibility, which helps maintain clarity and makes the system easier to extend.

---

## Key Strengths

### 1. Structured Pipeline Design

The system is built as a multi-stage pipeline where each component focuses on a single task.
This separation improves readability, maintainability, and scalability.

---

### 2. LLM Integration at Decision Points

LLMs are used where contextual reasoning adds value:

* generating effective search queries
* evaluating job relevance and constraints

The overall workflow remains controlled by application logic, keeping behavior predictable and easier to debug.

---

### 3. Cost-Aware Processing

Before sending data to the LLM, the system applies early filtering:

* removes duplicate URLs
* excludes senior-level roles
* filters out low-value domains

This reduces unnecessary LLM usage and improves efficiency.

---

### 4. Multi-Source Search Strategy

The system combines:

* **SerpAPI** → structured search results
* **Exa API** → semantic and long-tail discovery

This improves both precision and coverage.

---

### 5. Adaptive Scraping Strategy

Job pages often vary in structure and quality.

The system handles this by:

* using standard HTTP scraping first
* detecting low-quality or incomplete results
* retrying with browser automation when needed

This increases overall data reliability.

---

### 6. Fallback and Recovery Mechanism

Instead of failing silently, the system includes a recovery step:

* problematic pages are routed to a browser-based scraper
* results are reprocessed before evaluation

This makes the pipeline more robust in real-world scenarios.

---

### 7. Asynchronous Evaluation

The evaluation stage uses asynchronous processing with controlled concurrency:

* improves throughput
* respects API limits
* balances performance and cost

---

### 8. Practical Output (Google Sheets)

Results are exported into structured spreadsheets:

* separates valid jobs and manual-review jobs
* applies consistent formatting
* enables easy tracking and follow-up

---

## Core Components

* **JobPipeline**
  Orchestrates the entire workflow

* **QueryGenerator**
  Generates search queries using an LLM

* **SearchService**
  Integrates SerpAPI and Exa for job discovery on the internet

* **DataNormalizer**
  Converts raw results into a unified format

* **JobFilter**
  Applies early filtering rules

* **WebScraper**
  Performs initial scraping using HTTP requests

* **BrowserAutomation**
  Handles dynamic pages using Playwright

* **QualityChecker**
  Detects insufficient or low-quality content

* **JobEvaluator**
  Uses an LLM to evaluate job relevance

* **ExportService**
  Full automation of exporting results to Google Sheets

---

## Data Model

All data flows through a unified `Job` object:

```python
Job:
  - title
  - url
  - text
  - searched_via
  - keep
  - score
  - reason
  - is_ai_role
  - manual_check_required
  - date
```

---

## Tech Stack

* Python
* AsyncIO
* OpenAI API
* SerpAPI
* Exa API
* Playwright
* BeautifulSoup
* Requests
* gspread

---

## Current Limitations

* Prototype-oriented structure (needs modular refactor)
* LLM response parsing could be more robust
* Browser automation is sequential (performance can be improved)
* Configuration is partially hardcoded
* Limited automated testing

---

## Future Improvements

* Refactor into a modular `src/` structure
* Add CLI entry point for easier execution
* Improve logging and run summaries
* Add retry and error handling strategies
* Parallelize browser automation
* Introduce persistent storage (DB instead of Sheets)
* Expand evaluation with test datasets

---

## Getting Started

```bash
git clone https://github.com/mightyoctopus/automated-job-discovery-agentic-system
cd automated-job-discovery-agentic-system

pip install -r requirements.txt
```

Create a `.env` file:

```env
SERP_API_KEY=
EXA_API_KEY=
OPENAI_API_KEY=
JOB_SHEET_KEY=
```

Run the pipeline:

```bash
python main.py
```

---

## Summary

This project focuses on building a **practical, structured system** around LLM capabilities rather than relying on LLMs alone.

It demonstrates:

* pipeline-based system design
* effective integration of LLMs into real workflows
* cost-aware and resilient processing
* automation of a real-world task

---

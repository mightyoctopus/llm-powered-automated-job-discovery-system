import asyncio
from job_pipeline import JobPipeline


if __name__ == "__main__":
    app = JobPipeline(num_queries=6)
    asyncio.run(app.run())

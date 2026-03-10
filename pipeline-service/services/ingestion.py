import dlt
import requests
import os
import logging
from datetime import datetime

logger = logging.getLogger("pipeline-service.ingestion")

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")
DATABASE_URL = os.getenv("DATABASE_URL")

@dlt.resource(name="customers", write_disposition="merge", primary_key="customer_id")
def fetch_customers_resource():
    """
    DLT resource that fetches paginated data from the Flask mock server.
    """
    page = 1
    limit = 10
    
    logger.info(f"Starting resource fetch from {MOCK_SERVER_URL}")
    while True:
        try:
            url = f"{MOCK_SERVER_URL}/api/customers"
            params = {"page": page, "limit": limit}
            logger.debug(f"Fetching page {page} with limit {limit}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            payload = response.json()
            data = payload.get("data", [])
            
            if not data:
                logger.info("No more data to fetch.")
                break
            
            logger.info(f"Fetched {len(data)} records from page {page}")
            yield data
            
            total_pages = payload.get("total_pages", 0)
            if page >= total_pages:
                logger.debug(f"Reached total pages: {total_pages}")
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error to mock-server: {str(e)}")
            raise ConnectionError(f"Could not connect to Mock Server at {url}")

def start_ingestion():
    """
    Initializes and runs the dlt pipeline.
    """
    logger.info("Initializing DLT pipeline for customer ingestion")
    
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination="postgres",
        dataset_name="public" # load into the public schema directly
    )
    
    try:
        logger.info("Starting pipeline execution...")
        load_info = pipeline.run(fetch_customers_resource())
        
        # Extract total processed records
        total_records = 0
        for package in load_info.load_packages:
            for job in package.jobs["completed_jobs"]:
                if hasattr(job, 'metrics') and job.metrics:
                     total_records += job.metrics.get('row_count', 0)
        
        # fallback to trace if metrics not in load_packages
        if total_records == 0:
            total_records = pipeline.last_trace.last_extract_info.metrics.get('row_count', 0)

        logger.info(f"Ingestion successful. total_records processed: {total_records}")
        return total_records
    except Exception as e:
        logger.error(f"Pipeline execution failed critical error: {str(e)}", exc_info=True)
        raise

import dlt
import requests
import os
from datetime import datetime

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")
DATABASE_URL = os.getenv("DATABASE_URL")

@dlt.resource(name="customers", write_disposition="merge", primary_key="customer_id")
def fetch_customers_resource():
    """
    DLT resource that fetches paginated data from the Flask mock server.
    """
    page = 1
    limit = 10
    
    while True:
        try:
            url = f"{MOCK_SERVER_URL}/api/customers"
            params = {"page": page, "limit": limit}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            payload = response.json()
            data = payload.get("data", [])
            
            if not data:
                break
            
            # Data transformation: ensure date_of_birth is handled correctly if needed
            # dlt usually handles ISO strings well, but we can be explicit
            for record in data:
                if "date_of_birth" in record and record["date_of_birth"]:
                    try:
                        # dlt will handle this string as a date if it's in ISO format
                        pass 
                    except Exception:
                        pass
            
            yield data
            
            total_pages = payload.get("total_pages", 0)
            if page >= total_pages:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Connection error to mock-server: {e}")
            raise ConnectionError(f"Could not connect to Mock Server at {url}")

def start_ingestion():
    """
    Initializes and runs the dlt pipeline.
    """
    # dlt uses environment variables for credentials:
    # DESTINATION__POSTGRES__CREDENTIALS=postgresql://user:password@db:5432/customers_db
    # We should ensure this is set or pass it explicitly.
    
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination="postgres",
        dataset_name="public" # load into the public schema directly
    )
    
    try:
        load_info = pipeline.run(fetch_customers_resource())
        
        # Extract total processed records
        # dlt stores metrics in the trace for each job
        total_records = 0
        for package in load_info.load_packages:
            for job in package.jobs["completed_jobs"]:
                if hasattr(job, 'metrics') and job.metrics:
                     total_records += job.metrics.get('row_count', 0)
        
        # fallback to trace if metrics not in load_packages
        if total_records == 0:
            total_records = pipeline.last_trace.last_extract_info.metrics.get('row_count', 0)

        return total_records
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        raise

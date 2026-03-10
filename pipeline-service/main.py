import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pipeline-service")

from database import engine, get_db, Base
from models.customer import Customer
from services.ingestion import start_ingestion

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pipeline Service")

@app.get("/")
def read_root():
    logger.info("Health check endpoint called")
    return {"message": "Pipeline Service is running"}

@app.post("/api/ingest")
def ingest_data():
    """
    Endpoint to trigger the ingestion pipeline from the Mock Server.
    """
    try:
        records_processed = start_ingestion()
        return {
            "status": "success",
            "records_processed": int(records_processed)
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.get("/api/customers")
def list_customers(db: Session = Depends(get_db)):
    """
    Query the ingested data from the database.
    """
    customers = db.query(Customer).all()
    return customers

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

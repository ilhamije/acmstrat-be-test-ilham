import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

from database import get_db

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Pipeline Service is running"}

@patch("main.start_ingestion")
def test_ingest_data_success(mock_start_ingestion):
    # Mocking start_ingestion to return a row count
    mock_start_ingestion.return_value = 25
    
    response = client.post("/api/ingest")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "records_processed": 25
    }

@patch("main.start_ingestion")
def test_ingest_data_failure(mock_start_ingestion):
    # Mocking failure
    mock_start_ingestion.side_effect = Exception("Ingestion failed")
    
    response = client.post("/api/ingest")
    assert response.status_code == 500
    assert "Ingestion failed" in response.json()["detail"]

def test_list_customers():
    # Mock database session
    mock_db = MagicMock()
    
    # Mock query.all() to return a list
    mock_customer = MagicMock()
    mock_customer.customer_id = "CUST-001"
    # We must mock specific attributes that are returned in the response
    mock_customer.__dict__ = {
        "customer_id": "CUST-001",
        "first_name": "Test",
        "last_name": "User"
    }
    mock_db.query.return_value.all.return_value = [mock_customer]
    
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    
    try:
        response = client.get("/api/customers")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["customer_id"] == "CUST-001"
    finally:
        app.dependency_overrides.clear()

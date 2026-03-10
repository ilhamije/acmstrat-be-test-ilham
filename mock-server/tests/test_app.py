import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}

def test_get_customers_paginated(client):
    response = client.get('/api/customers?page=1&limit=5')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert len(data['data']) <= 5
    assert 'total' in data
    assert 'total_pages' in data

def test_get_single_customer_success(client):
    # Fetch first customer to get a valid ID
    res = client.get('/api/customers?limit=1')
    first_id = res.get_json()['data'][0]['customer_id']
    
    response = client.get(f'/api/customers/{first_id}')
    assert response.status_code == 200
    assert response.get_json()['customer_id'] == first_id

def test_get_single_customer_not_found(client):
    response = client.get('/api/customers/NON_EXISTENT_ID')
    assert response.status_code == 404
    assert 'error' in response.get_json()

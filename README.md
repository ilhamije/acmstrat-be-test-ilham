# Acumen Strategy - Data Pipeline Project

This project implements a high-performance data ingestion pipeline that fetches customer data from a mock Flask server, processes it using a FastAPI service with `dlt` (Data Load Tool), and upserts it into a PostgreSQL database.

## Project Architecture

- **Mock Server (Flask)**: Simulates an external API providing customer data as JSON with pagination support.
- **Pipeline Service (FastAPI)**: Orchestrates the ingestion process, fetches data from the Mock Server, and upserts it into PostgreSQL.
- **Database (PostgreSQL)**: Stores the ingested customer data in a strictly typed table.

## Data Flow

1. **Request**: User sends a `POST /api/ingest` request to the Pipeline Service.
2. **Fetch**: Pipeline Service fetches customer data from the Mock Server paginatedly.
3. **Load**: Data is transformed and upserted into PostgreSQL using `dlt` (merge strategy by `customer_id`).
4. **Respond**: Service returns the total count of processed records.

## Database Schema (`customers` table)

| Column | Type | Constraints |
| :--- | :--- | :--- |
| `customer_id` | `VARCHAR(50)` | PRIMARY KEY |
| `first_name` | `VARCHAR(100)` | NOT NULL |
| `last_name` | `VARCHAR(100)` | NOT NULL |
| `email` | `VARCHAR(255)` | NOT NULL |
| `phone` | `VARCHAR(20)` | |
| `address` | `TEXT` | |
| `date_of_birth` | `DATE` | |
| `account_balance` | `DECIMAL(15,2)` | |
| `created_at` | `TIMESTAMP` | |

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Services

1. Clone this repository.
2. Run the services using Docker Compose:
    ```bash
    docker-compose up --build -d
    ```
3. The services will be available at:
   - **Mock Server**: `http://localhost:5000`
   - **Pipeline Service**: `http://localhost:8000`
   - **PostgreSQL**: `localhost:5435` (Port mapped from 5432)

### Triggering Ingestion

Send a POST request to trigger the data pipeline:
```bash
curl -X POST http://localhost:8000/api/ingest
```

Expected Response:
```json
{
  "status": "success",
  "records_processed": 25
}
```

## Testing

Each service contains its own test suite using `pytest`.

### Mock Server Tests
```bash
cd mock-server
pytest
```

### Pipeline Service Tests
```bash
cd pipeline-service
pytest
```

## Project Structure

```
├── docker-compose.yml              # Service orchestration
├── mock-server/                    # Flask Mock Server
│   ├── app.py                      # Flask Application logic
│   ├── data/                       # JSON data source
│   └── tests/                      # Mock Server Unit Tests
├── pipeline-service/               # FastAPI Ingestion Service
│   ├── main.py                     # FastAPI Application core
│   ├── models/                     # SQLAlchemy Models
│   ├── services/                   # Ingestion logic (dlt pipeline)
│   ├── tests/                      # Pipeline Service Unit Tests
│   └── database.py                 # Database connectivity
└── README.md                       # This documentation
```
# acmstrat-be-test-ilham

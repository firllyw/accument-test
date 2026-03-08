# Data Pipeline Project

This project implements a data pipeline using Docker, consisting of:
1. **Flask API**: Serves mock customer data from a JSON file.
2. **FastAPI Ingestion Service**: Ingests data from the Flask API using `dlt` (Data Load Tool) and stores it in PostgreSQL.
3. **PostgreSQL**: Stores the ingested customer data.

## Prerequisites
- Docker Desktop (running)
- Python 3.10+
- Git

## Running the Project

1. Start all services using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

2. Check if services are running:
   ```bash
   docker-compose ps
   ```

## Testing

Test the Flask mock server (returns paginated mock data):
```bash
curl "http://localhost:5000/api/customers?page=1&limit=5"
```

Trigger the FastAPI ingestion pipeline (pulls from Flask and upserts to Postgres):
```bash
curl -X POST http://localhost:8000/api/ingest
```

Test the FastAPI customers endpoint (reads from PostgreSQL):
```bash
curl "http://localhost:8000/api/customers?page=1&limit=5"
```

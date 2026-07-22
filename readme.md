# Setu Payment Service

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker

## Setup

1. Clone the repository.
2. Create a PostgreSQL database named `setu`.
3. Copy `.env.example` to `.env` and update the connection string.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

## Endpoints

- POST `/events`
- POST `/events/bulk`
- GET `/transactions`
- GET `/transactions/{transaction_id}`
- GET `/reconciliation/summary`
- GET `/reconciliation/discrepancies`

## Import Sample Data

```bash
python import_events.py
```

This loads the contents of `sample_events.json` using the bulk endpoint.
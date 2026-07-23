# Setu Payment Service

A production-minded backend service built with **FastAPI** and **PostgreSQL** for ingesting payment lifecycle events, maintaining transaction state, and providing reconciliation APIs for operations teams.

---

## Live Demo

**API Base URL**

https://setuassesment.onrender.com

**Swagger UI**

https://setuassesment.onrender.com/docs

---

# Features

- Idempotent payment event ingestion
- Transaction lifecycle management
- Complete event history tracking
- Merchant-wise transaction management
- SQL-based filtering and pagination
- Reconciliation summary reporting
- Discrepancy detection
- PostgreSQL-backed persistent storage
- Public deployment on Render

---

# Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Deployment | Render |
| API Documentation | Swagger / OpenAPI |

---

# Architecture Overview

```
                Payment Systems
                       │
                       ▼
              POST /events
                       │
                       ▼
              FastAPI Application
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
 Event History   Transaction State   Merchant Data
                       │
                       ▼
                PostgreSQL Database
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
 GET /transactions   GET /summary   GET /discrepancies
```

---

# Database Schema

The service consists of four primary tables.

## Merchants

Stores merchant information.

- merchant_id
- merchant_name

---

## Transactions

Stores the latest state of every transaction.

- transaction_id
- merchant_id
- amount
- currency
- current_status
- payment_status
- settlement_status
- timestamps

---

## Payment Events

Stores every incoming payment lifecycle event.

- event_id (Unique)
- transaction_id
- event_type
- timestamp
- raw_event

---

## Reconciliation Status

Tracks reconciliation state.

- transaction_id
- is_reconciled
- discrepancy_reason

---

# API Endpoints

## POST /events

Ingest a payment lifecycle event.

Supports

- payment_initiated
- payment_processed
- payment_failed
- settled

Duplicate event IDs are ignored to ensure idempotency.

---

## POST /events/bulk

Bulk import payment events from the provided `sample_events.json`.

---

## GET /transactions

Retrieve transactions with support for

- merchant filtering
- status filtering
- date range filtering
- pagination
- sorting

---

## GET /transactions/{transaction_id}

Returns

- transaction details
- current status
- merchant information
- complete event history

---

## GET /reconciliation/summary

Returns reconciliation summaries grouped by merchant.

---

## GET /reconciliation/discrepancies

Returns inconsistent transactions including

- processed but not settled
- settlement after failure
- conflicting state transitions

---

# Local Setup

## Clone Repository

```bash
git clone <repository-url>
cd setu-payment-service
```

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment

Create a `.env` file.

```
DATABASE_URL=postgresql://username:password@localhost:5432/setu
API_BASE_URL=http://127.0.0.1:8000
```

## Run Application

```bash
uvicorn main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# Loading Sample Data

The assignment-provided `sample_events.json` contains approximately **10,000 payment events** across multiple merchants.

Import it using:

```bash
python import_events.py
```

The script sends events to the `/events/bulk` endpoint to populate the database while exercising the same validation and idempotency logic used by the application.

---

# Deployment

The application is deployed on **Render**.

Deployment includes:

- FastAPI Web Service
- PostgreSQL Database
- Environment Variables
- Automatic GitHub Deployment

Public URL

```
https://setuassesment.onrender.com
```

---

# Idempotency Strategy

Each incoming event contains a unique **event_id**.

A unique database constraint ensures duplicate events are rejected before altering transaction state.

This guarantees:

- repeated requests are safe
- transaction state remains consistent
- complete event history is preserved

---

# Database Design Decisions

Several design choices were made to keep the system simple, scalable, and efficient.

- Event history is stored separately from transaction state to preserve a complete audit trail.
- Transactions maintain only the latest state, allowing fast lookup without replaying all events.
- Merchants are normalized into a dedicated table to avoid redundant data.
- Reconciliation status is stored independently to simplify reporting queries.
- SQL filtering, pagination, and aggregation are performed in the database instead of Python for better performance.

---

# Indexing Strategy

Indexes were created for commonly queried columns including:

- event_id (Unique)
- transaction_id
- merchant_id
- event_timestamp
- current_status

These indexes improve lookup speed, filtering, and reconciliation queries.

---

# Assumptions

- Event IDs are globally unique.
- Events may arrive more than once.
- Transactions can receive multiple lifecycle events.
- Settlement events may arrive after payment events.
- Merchants are uniquely identified by merchant_id.

---

# Tradeoffs

To keep the assignment focused and easy to review, a few practical tradeoffs were made.

- Authentication and authorization were not implemented because they were outside the assignment scope.
- Database migrations (e.g., Alembic) were omitted, and tables are created automatically at startup for simpler setup.
- Reconciliation rules cover the scenarios described in the assignment; a production system would likely support configurable business rules.
- Bulk event ingestion is implemented synchronously. For much larger datasets, asynchronous processing with a message queue (such as Kafka or RabbitMQ) would improve throughput and resilience.
- Logging and monitoring are kept minimal. In production, structured logging, metrics, and tracing would be added.

---

# Future Improvements

Given more time, the following enhancements would be considered:

- Alembic database migrations
- JWT authentication
- Background workers for bulk ingestion
- Docker Compose for local development
- Automated unit and integration tests
- Redis caching
- CI/CD pipeline
- Prometheus and Grafana monitoring

---

# Testing

The project includes

- Public deployment
- Swagger UI
- Postman Collection
- Screen-recorded API walkthrough

---

# AI Usage Disclosure

AI tools (ChatGPT) were used to assist with brainstorming, documentation refinement, debugging, and code review. All implementation decisions, testing, integration, and final validation were completed manually.

---


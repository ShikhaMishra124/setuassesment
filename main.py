from typing import List
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
import models
import schemas
import services

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Setu Payment Service",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Home


@app.get("/")
def home():
    return {
        "message": "Setu Payment Service is running"
    }



# Ingest Single Event


@app.post("/events")
def ingest_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db)
):
    return services.ingest_event(db, event)



# Bulk Import


@app.post("/events/bulk")
def bulk_import(
    events: List[schemas.EventCreate],
    db: Session = Depends(get_db)
):
    return services.bulk_import(db, events)



# List Transactions


@app.get("/transactions")
def list_transactions(
    merchant_id: str | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    return services.get_transactions(
        db=db,
        merchant_id=merchant_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit,
    )



# Transaction Details


@app.get("/transactions/{transaction_id}")
def transaction_details(
    transaction_id: str,
    db: Session = Depends(get_db)
):

    data = services.transaction_details(db, transaction_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return data



# Reconciliation Summary


@app.get("/reconciliation/summary")
def reconciliation_summary(
    db: Session = Depends(get_db)
):
    return services.reconciliation_summary(db)



# Reconciliation Discrepancies


@app.get("/reconciliation/discrepancies")
def discrepancies(
    db: Session = Depends(get_db)
):
    return services.discrepancies(db)
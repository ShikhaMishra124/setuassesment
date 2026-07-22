from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas



# INGEST SINGLE EVENT


def ingest_event(db: Session, event: schemas.EventCreate):

    # Idempotency check
    existing = (
        db.query(models.PaymentEvent)
        .filter(models.PaymentEvent.event_id == event.event_id)
        .first()
    )

    if existing:
        return {"message": "Duplicate event ignored"}

    # Merchant
    merchant = (
        db.query(models.Merchant)
        .filter(models.Merchant.merchant_code == event.merchant_id)
        .first()
    )

    if not merchant:
        merchant = models.Merchant(
            merchant_code=event.merchant_id,
            merchant_name=event.merchant_name,
        )

        db.add(merchant)
        db.commit()
        db.refresh(merchant)

    # Transaction
    txn = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == event.transaction_id)
        .first()
    )

    if txn is None:

        payment_status = "initiated"
        settlement_status = "pending"

        if event.event_type == "payment_processed":
            payment_status = "processed"

        elif event.event_type == "payment_failed":
            payment_status = "failed"

        elif event.event_type == "settled":
            payment_status = "processed"
            settlement_status = "settled"

        txn = models.Transaction(
            transaction_id=event.transaction_id,
            merchant_id=merchant.id,
            amount=event.amount,
            currency=event.currency,
            payment_status=payment_status,
            settlement_status=settlement_status,
            current_status=event.event_type,
            last_event_timestamp=event.timestamp,
        )

        db.add(txn)

    else:

        txn.current_status = event.event_type
        txn.last_event_timestamp = event.timestamp

        if event.event_type == "payment_initiated":
            txn.payment_status = "initiated"

        elif event.event_type == "payment_processed":
            txn.payment_status = "processed"

        elif event.event_type == "payment_failed":
            txn.payment_status = "failed"

        elif event.event_type == "settled":
            txn.settlement_status = "settled"

    # Save event history
    payment_event = models.PaymentEvent(
        event_id=event.event_id,
        transaction_id=event.transaction_id,
        merchant_id=merchant.id,
        event_type=event.event_type,
        amount=event.amount,
        currency=event.currency,
        event_timestamp=event.timestamp,
        raw_event=event.model_dump(mode="json"),
    )

    db.add(payment_event)

    db.commit()

    return {"message": "Event stored successfully"}



# BULK IMPORT


def bulk_import(db: Session, events):

    imported = 0
    duplicates = 0

    for event in events:

        result = ingest_event(db, event)

        if result["message"] == "Duplicate event ignored":
            duplicates += 1
        else:
            imported += 1

    return {
        "imported": imported,
        "duplicates": duplicates
    }



# GET TRANSACTIONS


def get_transactions(
    db,
    merchant_id=None,
    status=None,
    start_date=None,
    end_date=None,
    page=1,
    limit=10,
):

    query = db.query(models.Transaction)

    if merchant_id:

        merchant = (
            db.query(models.Merchant)
            .filter(models.Merchant.merchant_code == merchant_id)
            .first()
        )

        if merchant:
            query = query.filter(
                models.Transaction.merchant_id == merchant.id
            )

    if status:
        query = query.filter(
            models.Transaction.current_status == status
        )

    if start_date:
        query = query.filter(
            models.Transaction.last_event_timestamp >= start_date
        )

    if end_date:
        query = query.filter(
            models.Transaction.last_event_timestamp <= end_date
        )

    return (
        query.order_by(models.Transaction.last_event_timestamp.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )



# TRANSACTION DETAILS


def transaction_details(db, transaction_id):

    txn = (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )

    if txn is None:
        return None

    merchant = (
        db.query(models.Merchant)
        .filter(models.Merchant.id == txn.merchant_id)
        .first()
    )

    events = (
        db.query(models.PaymentEvent)
        .filter(models.PaymentEvent.transaction_id == transaction_id)
        .order_by(models.PaymentEvent.event_timestamp)
        .all()
    )

    return {
        "transaction": txn,
        "merchant": merchant,
        "events": events,
    }



# RECONCILIATION SUMMARY


from sqlalchemy import func

def reconciliation_summary(db):

    results = (
        db.query(
            models.Merchant.merchant_name.label("merchant_name"),
            func.count(models.Transaction.id).label("transactions"),
            func.sum(models.Transaction.amount).label("amount"),
        )
        .join(
            models.Transaction,
            models.Transaction.merchant_id == models.Merchant.id,
        )
        .group_by(models.Merchant.merchant_name)
        .all()
    )

    response = []

    for row in results:
        response.append(
            {
                "merchant_name": row.merchant_name,
                "transactions": row.transactions,
                "amount": float(row.amount),
            }
        )

    return response


# DISCREPANCIES


def discrepancies(db):

    transactions = db.query(models.Transaction).all()

    response = []

    for txn in transactions:

        reason = None

        if (
            txn.payment_status == "processed"
            and txn.settlement_status != "settled"
        ):
            reason = "Processed but not settled"

        elif (
            txn.payment_status == "failed"
            and txn.settlement_status == "settled"
        ):
            reason = "Failed payment settled"

        if reason:
            response.append(
                {
                    "transaction_id": txn.transaction_id,
                    "reason": reason,
                }
            )

    return response
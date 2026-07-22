from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    BigInteger,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_code = Column(String, unique=True, nullable=False)
    merchant_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="merchant")
    events = relationship("PaymentEvent", back_populates="merchant")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    transaction_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    merchant_id = Column(
        BigInteger,
        ForeignKey("merchants.id"),
        nullable=False,
    )

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, nullable=False)

    payment_status = Column(String, nullable=False)
    settlement_status = Column(String, nullable=False)
    current_status = Column(String, nullable=False)

    initiated_at = Column(DateTime)
    processed_at = Column(DateTime)
    failed_at = Column(DateTime)
    settled_at = Column(DateTime)

    last_event_timestamp = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="transactions")
    events = relationship(
        "PaymentEvent",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    event_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transactions.transaction_id"),
        nullable=False,
    )

    merchant_id = Column(
        BigInteger,
        ForeignKey("merchants.id"),
        nullable=False,
    )

    event_type = Column(String, nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, nullable=False)

    event_timestamp = Column(DateTime, nullable=False)

    raw_event = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="events")
    transaction = relationship("Transaction", back_populates="events")


class ReconciliationStatus(Base):
    __tablename__ = "reconciliation_status"

    transaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transactions.transaction_id"),
        primary_key=True,
    )

    is_reconciled = Column(default=False)
    discrepancy_reason = Column(String)
    last_checked_at = Column(DateTime)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


Index("idx_transaction_id", Transaction.transaction_id)
Index("idx_event_id", PaymentEvent.event_id)
Index("idx_event_timestamp", PaymentEvent.event_timestamp)
Index("idx_merchant_code", Merchant.merchant_code)
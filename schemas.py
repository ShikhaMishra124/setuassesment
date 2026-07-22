from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional


#  Event 

class EventCreate(BaseModel):
    event_id: UUID
    event_type: str
    transaction_id: UUID
    merchant_id: str
    merchant_name: str
    amount: Decimal
    currency: str
    timestamp: datetime


#  Merchant 

class MerchantResponse(BaseModel):
    merchant_code: str
    merchant_name: str

    class Config:
        from_attributes = True


#  Transaction 

class TransactionResponse(BaseModel):
    transaction_id: UUID
    amount: Decimal
    currency: str

    payment_status: str
    settlement_status: str
    current_status: str

    last_event_timestamp: datetime

    class Config:
        from_attributes = True


#  Event History 

class EventHistory(BaseModel):
    event_id: UUID
    event_type: str
    event_timestamp: datetime

    class Config:
        from_attributes = True


#  Transaction Details 

class TransactionDetails(BaseModel):
    transaction: TransactionResponse
    merchant: MerchantResponse
    events: list[EventHistory]


#  Reconciliation 

class DiscrepancyResponse(BaseModel):
    transaction_id: UUID
    reason: str
from datetime import date, time
from pydantic import BaseModel, Field

from app.enums import BookingStatus, Intent


class IntentResult(BaseModel):
    intent: Intent
    bike_model: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class BikeOut(BaseModel):
    model_code: str
    model_name: str
    variant: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class PriceOut(BaseModel):
    model_code: str
    model_name: str
    price_available: bool
    price: float | None = None
    currency: str | None = None
    message: str


class AvailabilityOut(BaseModel):
    model_code: str
    location: str
    date: date
    requested_time: time
    available: bool
    alternative_times: list[time] = []


class BookingCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=160)
    customer_phone: str = Field(min_length=5, max_length=40)
    model_code: str = Field(min_length=1, max_length=80)
    preferred_date: date
    preferred_time: time
    location: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=8, max_length=128)
    confirmed: bool = False


class BookingOut(BaseModel):
    booking_id: str
    status: BookingStatus | str
    customer_name: str
    customer_phone: str
    model_code: str
    preferred_date: date
    preferred_time: time
    location: str
    duplicate_replay: bool = False


class HandoffRequest(BaseModel):
    conversation_id: str
    customer_phone: str | None = None
    current_intent: Intent | None = None
    selected_model: str | None = None
    current_step: str | None = None
    reason: str
    conversation_summary: str


class HandoffResponse(BaseModel):
    accepted: bool
    queue: str
    message: str

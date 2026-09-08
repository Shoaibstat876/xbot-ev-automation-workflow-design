import uuid
from datetime import datetime, date, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.enums import BookingStatus


class BikeModel(Base):
    __tablename__ = "bike_models"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    model_name: Mapped[str] = mapped_column(String(160))
    variant: Mapped[str | None] = mapped_column(String(160), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    availability: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestRideBooking(Base):
    __tablename__ = "test_ride_bookings"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_booking_idempotency_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    booking_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        default=lambda: f"TR-{uuid.uuid4().hex[:10].upper()}",
    )
    customer_name: Mapped[str] = mapped_column(String(160))
    customer_phone: Mapped[str] = mapped_column(String(40))
    bike_model_id: Mapped[int] = mapped_column(ForeignKey("bike_models.id"))
    preferred_date: Mapped[date] = mapped_column(Date)
    preferred_time: Mapped[time] = mapped_column(Time)
    location: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), default=BookingStatus.CONFIRMED.value)
    channel: Mapped[str] = mapped_column(String(40), default="WHATSAPP")
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bike_model: Mapped[BikeModel] = relationship()


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(80), index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80))
    intent: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tool_called: Mapped[str | None] = mapped_column(String(120), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_type: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

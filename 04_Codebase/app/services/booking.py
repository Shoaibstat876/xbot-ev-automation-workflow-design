from datetime import date, time
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.enums import BookingStatus
from app.models import TestRideBooking
from app.schemas import AvailabilityOut, BookingCreate, BookingOut
from app.services.catalog import get_model_by_code


def check_availability(
    db: Session,
    *,
    model_code: str,
    location: str,
    preferred_date: date,
    preferred_time: time,
) -> AvailabilityOut:
    model = get_model_by_code(db, model_code)
    if not model:
        raise ValueError("INVALID_MODEL")

    if preferred_date < date.today():
        raise ValueError("PAST_DATE")

    existing = db.scalar(
        select(TestRideBooking).where(
            TestRideBooking.bike_model_id == model.id,
            TestRideBooking.location == location,
            TestRideBooking.preferred_date == preferred_date,
            TestRideBooking.preferred_time == preferred_time,
            TestRideBooking.status == BookingStatus.CONFIRMED.value,
        )
    )

    # No showroom hours or real scheduling rules were supplied in the source material.
    # Therefore this reference implementation only checks for a conflicting confirmed booking.
    return AvailabilityOut(
        model_code=model.model_code,
        location=location,
        date=preferred_date,
        requested_time=preferred_time,
        available=existing is None,
        alternative_times=[],
    )


def create_booking(db: Session, payload: BookingCreate) -> BookingOut:
    if not payload.confirmed:
        raise ValueError("EXPLICIT_CONFIRMATION_REQUIRED")

    if payload.preferred_date < date.today():
        raise ValueError("PAST_DATE")

    model = get_model_by_code(db, payload.model_code)
    if not model:
        raise ValueError("INVALID_MODEL")

    # Idempotent replay protection.
    existing_by_key = db.scalar(
        select(TestRideBooking).where(
            TestRideBooking.idempotency_key == payload.idempotency_key
        )
    )
    if existing_by_key:
        return BookingOut(
            booking_id=existing_by_key.booking_id,
            status=existing_by_key.status,
            customer_name=existing_by_key.customer_name,
            customer_phone=existing_by_key.customer_phone,
            model_code=model.model_code,
            preferred_date=existing_by_key.preferred_date,
            preferred_time=existing_by_key.preferred_time,
            location=existing_by_key.location,
            duplicate_replay=True,
        )

    availability = check_availability(
        db,
        model_code=payload.model_code,
        location=payload.location,
        preferred_date=payload.preferred_date,
        preferred_time=payload.preferred_time,
    )
    if not availability.available:
        raise ValueError("SLOT_UNAVAILABLE")

    booking = TestRideBooking(
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        bike_model_id=model.id,
        preferred_date=payload.preferred_date,
        preferred_time=payload.preferred_time,
        location=payload.location,
        status=BookingStatus.CONFIRMED.value,
        idempotency_key=payload.idempotency_key,
    )
    db.add(booking)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Another identical request may have won the race.
        replay = db.scalar(
            select(TestRideBooking).where(
                TestRideBooking.idempotency_key == payload.idempotency_key
            )
        )
        if replay:
            return BookingOut(
                booking_id=replay.booking_id,
                status=replay.status,
                customer_name=replay.customer_name,
                customer_phone=replay.customer_phone,
                model_code=model.model_code,
                preferred_date=replay.preferred_date,
                preferred_time=replay.preferred_time,
                location=replay.location,
                duplicate_replay=True,
            )
        raise

    db.refresh(booking)

    return BookingOut(
        booking_id=booking.booking_id,
        status=booking.status,
        customer_name=booking.customer_name,
        customer_phone=booking.customer_phone,
        model_code=model.model_code,
        preferred_date=booking.preferred_date,
        preferred_time=booking.preferred_time,
        location=booking.location,
        duplicate_replay=False,
    )


def get_booking(db: Session, booking_id: str) -> TestRideBooking | None:
    return db.scalar(
        select(TestRideBooking).where(TestRideBooking.booking_id == booking_id)
    )


def cancel_booking(db: Session, booking_id: str) -> TestRideBooking | None:
    booking = get_booking(db, booking_id)
    if not booking:
        return None

    if booking.status == BookingStatus.CANCELLED.value:
        return booking

    booking.status = BookingStatus.CANCELLED.value
    db.commit()
    db.refresh(booking)
    return booking

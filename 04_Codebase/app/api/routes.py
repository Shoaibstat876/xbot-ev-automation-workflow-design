import uuid
from datetime import date, time

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.enums import BookingStatus
from app.integrations.n8n import notify_booking_created
from app.integrations.twilio import verify_twilio_signature
from app.schemas import (
    AvailabilityOut,
    BikeOut,
    BookingCreate,
    BookingOut,
    HandoffRequest,
    HandoffResponse,
    IntentResult,
    PriceOut,
)
from app.services.booking import cancel_booking, check_availability, create_booking, get_booking
from app.services.catalog import get_model_by_code, list_active_models
from app.services.intent_router import route_intent


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@router.get("/api/bikes", response_model=list[BikeOut])
def bikes(db: Session = Depends(get_db)):
    return list_active_models(db)


@router.get("/api/bikes/{model_code}/price", response_model=PriceOut)
def bike_price(model_code: str, db: Session = Depends(get_db)):
    model = get_model_by_code(db, model_code)
    if not model:
        raise HTTPException(status_code=404, detail="Bike model not recognized.")

    if model.price is None or not model.currency:
        return PriceOut(
            model_code=model.model_code,
            model_name=model.model_name,
            price_available=False,
            price=None,
            currency=model.currency,
            message="Verified price is currently unavailable. Please contact human support.",
        )

    return PriceOut(
        model_code=model.model_code,
        model_name=model.model_name,
        price_available=True,
        price=float(model.price),
        currency=model.currency,
        message="Official price retrieved from backend source of truth.",
    )


@router.get("/api/test-rides/availability", response_model=AvailabilityOut)
def availability(
    model_code: str,
    location: str,
    preferred_date: date,
    preferred_time: time,
    db: Session = Depends(get_db),
):
    try:
        return check_availability(
            db,
            model_code=model_code,
            location=location,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "INVALID_MODEL":
            raise HTTPException(status_code=404, detail="Bike model not recognized.")
        if code == "PAST_DATE":
            raise HTTPException(status_code=422, detail="Preferred date must be today or later.")
        raise


@router.post("/api/test-rides", response_model=BookingOut, status_code=201)
def book_test_ride(payload: BookingCreate, db: Session = Depends(get_db)):
    try:
        result = create_booking(db, payload)
    except ValueError as exc:
        code = str(exc)
        mapping = {
            "EXPLICIT_CONFIRMATION_REQUIRED": (409, "Explicit customer confirmation is required."),
            "PAST_DATE": (422, "Preferred date must be today or later."),
            "INVALID_MODEL": (404, "Bike model not recognized."),
            "SLOT_UNAVAILABLE": (409, "Requested test-ride slot is unavailable."),
        }
        status_code, detail = mapping.get(code, (400, "Booking could not be completed."))
        raise HTTPException(status_code=status_code, detail=detail)

    # Downstream notification is deliberately separate from booking state.
    try:
        notify_booking_created(result.model_dump(mode="json"))
    except Exception:
        # In production, log and retry asynchronously.
        pass

    return result


@router.get("/api/test-rides/{booking_id}", response_model=BookingOut)
def read_booking(booking_id: str, db: Session = Depends(get_db)):
    booking = get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    return BookingOut(
        booking_id=booking.booking_id,
        status=booking.status,
        customer_name=booking.customer_name,
        customer_phone=booking.customer_phone,
        model_code=booking.bike_model.model_code,
        preferred_date=booking.preferred_date,
        preferred_time=booking.preferred_time,
        location=booking.location,
    )


@router.post("/api/test-rides/{booking_id}/cancel", response_model=BookingOut)
def cancel_test_ride(booking_id: str, db: Session = Depends(get_db)):
    booking = cancel_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    return BookingOut(
        booking_id=booking.booking_id,
        status=booking.status,
        customer_name=booking.customer_name,
        customer_phone=booking.customer_phone,
        model_code=booking.bike_model.model_code,
        preferred_date=booking.preferred_date,
        preferred_time=booking.preferred_time,
        location=booking.location,
    )


@router.post("/api/handoff", response_model=HandoffResponse)
def handoff(payload: HandoffRequest):
    # Replace with a real CRM/support queue integration when available.
    return HandoffResponse(
        accepted=True,
        queue=settings.human_support_queue,
        message="Handoff context accepted by the reference backend.",
    )


@router.post("/api/intent", response_model=IntentResult)
def intent(message: str):
    return route_intent(message)


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    request: Request,
    body: str = Form(default=""),
    from_number: str = Form(default="", alias="From"),
    x_twilio_signature: str | None = Header(default=None),
):
    form = dict(await request.form())

    if not verify_twilio_signature(
        request_url=str(request.url),
        form_data={k: str(v) for k, v in form.items()},
        signature=x_twilio_signature,
    ):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature.")

    result = route_intent(body)

    return {
        "request_id": str(uuid.uuid4()),
        "from": from_number,
        "intent": result.intent,
        "confidence": result.confidence,
        "note": (
            "Reference webhook only. Connect conversation-state management and "
            "Twilio response formatting before production use."
        ),
    }

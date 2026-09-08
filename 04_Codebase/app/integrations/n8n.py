import httpx

from app.config import settings


def notify_booking_created(payload: dict) -> bool:
    """
    Optional downstream integration only.

    Booking state has already been committed before this function is called.
    A notification failure must never create a second booking.
    """
    if not settings.n8n_booking_webhook_url:
        return False

    response = httpx.post(
        settings.n8n_booking_webhook_url,
        json=payload,
        timeout=10.0,
    )
    response.raise_for_status()
    return True

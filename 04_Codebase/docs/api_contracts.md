# Conceptual Tool / API Contracts

## `get_bike_models()`

Purpose:
Return approved active bike models.

Input:
None.

Validation:
Only active catalog rows are returned.

Output:
Model code, name, variant.

Failure:
Safe backend error; do not invent models.

---

## `get_bike_price(model_code)`

Purpose:
Return official backend price.

Input:
Validated model code.

Validation:
Model must exist and be active.

Output:
Price availability, exact price, currency.

Failure:
If price is missing, return unavailable; do not guess.

---

## `get_available_test_ride_slots(model_code, location, date)`

Purpose:
Return available test-ride slots.

Input:
Model, location, future date.

Validation:
Model exists; date valid; production implementation should enforce approved operating hours.

Output:
Available slots.

Failure:
Safe unavailable/error response.

---

## `create_test_ride_booking(...)`

Purpose:
Create a confirmed booking.

Input:
Customer name, channel phone, model, location, date, time, idempotency key, `confirmed=true`.

Validation:
- explicit confirmation required
- model valid
- date not in past
- slot available
- idempotency key unique

Output:
Booking ID, status.

Failure:
No fake confirmation.

---

## `get_booking(booking_id)`

Purpose:
Read authoritative booking state.

---

## `cancel_booking(booking_id)`

Purpose:
Cancel an existing booking safely.

---

## `handoff_to_human(...)`

Purpose:
Transfer the case with context.

Payload:
- conversation ID
- customer phone where appropriate
- current intent
- selected model
- current step
- escalation reason
- conversation summary

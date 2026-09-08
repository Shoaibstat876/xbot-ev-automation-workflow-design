# XBOT EV — Task 3 Reference Codebase

This repository is an **implementation-ready reference scaffold** derived from the Task 3 workflow/design artifacts.

It is intentionally honest about scope:

- The original Task 3 is a **workflow design** assessment.
- This codebase demonstrates how the proposed architecture can be translated into a backend project.
- It does **not** claim that Twilio, OpenAI, Google Calendar, n8n, CRM, or a production PostgreSQL instance are already connected.
- No official XBOT EV model names, prices, showroom locations, or operating hours are invented here.
- The backend remains the authority for business rules; the AI layer must never invent official price, availability, booking IDs, or booking success.

## Architecture

Customer
→ WhatsApp
→ Twilio webhook
→ FastAPI
→ intent router
→ catalog / booking services
→ PostgreSQL
→ optional integrations
→ customer response / human handoff

## Core design rules implemented

1. **Two top-level intents**
   - `PRICE_QUERY`
   - `BOOK_TEST_RIDE`

2. **Controlled intent set**
   - `PRICE_QUERY`
   - `BOOK_TEST_RIDE`
   - `HELP`
   - `CANCEL`
   - `HUMAN_HANDOFF`
   - `UNKNOWN`

3. **Price source of truth**
   - Price comes from the `bike_models` table.
   - If a verified price is unavailable, the API returns a safe unavailable response.
   - The AI never fabricates a price.

4. **Server-side booking persistence**
   - Bookings are stored in PostgreSQL.
   - Browser `localStorage` / `sessionStorage` are not used as the booking source of truth.

5. **Explicit confirmation gate**
   - Draft data can be collected first.
   - A booking is only created after `confirmed=true`.

6. **Duplicate protection**
   - `idempotency_key` is unique.
   - A retry returns the existing booking rather than creating a second booking.

7. **Safe failure semantics**
   - Booking creation failure never returns a fake confirmation.
   - Notification failure is separate from booking state.

8. **Human handoff**
   - Handoff payload includes conversation context and escalation reason.

## Project structure

```text
app/
  api/
  integrations/
  services/
  config.py
  db.py
  enums.py
  logging_config.py
  main.py
  models.py
  schemas.py
docs/
  architecture.md
  api_contracts.md
  master_workflow.mmd
tests/
.env.example
docker-compose.yml
requirements.txt
```

## Quick start

### 1. Create environment file

Copy:

```bash
cp .env.example .env
```

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

### 3. Create virtual environment

```bash
python -m venv .venv
```

Activate it, then:

```bash
pip install -r requirements.txt
```

### 4. Run API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Important setup note

The database starts empty. Add only **approved XBOT EV catalog data** before using price endpoints.

Do not hard-code unverified prices into prompts, frontend code, or seed files.

## Main endpoints

- `GET /health`
- `GET /api/bikes`
- `GET /api/bikes/{model_code}/price`
- `GET /api/test-rides/availability`
- `POST /api/test-rides`
- `GET /api/test-rides/{booking_id}`
- `POST /api/test-rides/{booking_id}/cancel`
- `POST /api/handoff`
- `POST /webhooks/whatsapp`

## Production work still required

Before calling this production-ready, add:

- real approved XBOT EV bike catalog
- real dealer/location data
- real operating-hours rules
- Twilio sender configuration
- secure webhook signature settings
- production PostgreSQL
- production migrations
- authentication/authorization for internal/admin APIs
- real availability engine or calendar integration
- OpenAI credentials if AI intent routing is enabled
- n8n / CRM integrations if required
- monitoring/alerting
- PII retention policy
- load/security testing

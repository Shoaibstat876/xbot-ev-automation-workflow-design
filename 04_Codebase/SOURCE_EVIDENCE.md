# Source Evidence Used

This reference codebase was generated from the user's Task 3 working artifacts.

Key source-derived requirements represented here include:

- Mermaid workflow containing:
  - WhatsApp entry
  - FastAPI validation
  - PostgreSQL
  - price flow
  - test-ride flow
  - explicit confirmation
  - duplicate request check
  - fallback
  - human handoff

- Fallback / edge-case notes:
  - invalid model
  - price unavailable
  - invalid date/time
  - cancellation
  - duplicate confirmation
  - booking failure
  - notification failure
  - repeated misunderstanding
  - human request

- Proposed tool/API stack:
  - Twilio WhatsApp API
  - FastAPI + Python
  - PostgreSQL
  - OpenAI structured outputs
  - n8n
  - optional Google Calendar / internal slots
  - structured logging
  - secret management
  - human support queue

- Security / governance:
  - HTTPS
  - webhook verification
  - secrets server-side
  - minimum required PII
  - least privilege
  - validation / rate limiting
  - retention
  - AI action boundaries
  - auditability

This package does not silently invent official XBOT EV prices, models, locations, or operating hours.

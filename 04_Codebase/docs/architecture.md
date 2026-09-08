# Architecture Notes

## Responsibility boundaries

### Channel
**Twilio WhatsApp API**

- receives/sends WhatsApp messages
- forwards inbound messages to the FastAPI webhook
- does not own pricing or booking state

### Backend
**FastAPI + Python**

Owns:
- request validation
- intent orchestration
- model validation
- price retrieval
- date/time validation
- availability checks
- explicit confirmation gate
- booking creation
- cancellation
- duplicate protection
- human handoff payload

### AI/NLP
**OpenAI structured output — proposed integration**

May:
- classify natural-language intent
- extract model/date/time wording

Must not:
- invent official price
- invent available slots
- generate booking IDs
- directly mutate authoritative business state
- claim booking success without backend confirmation

### Persistence
**PostgreSQL**

Authoritative for:
- bike catalog
- official pricing
- bookings
- booking status
- slot-conflict checks
- audit events

### n8n
Secondary workflow orchestration only:
- dealer notifications
- CRM sync
- email
- follow-up

It is not the booking source of truth.

## Session state vs persistent state

Conversation/session state can temporarily hold:
- current intent
- selected model
- preferred location
- preferred date
- preferred time
- current step
- fallback count
- confirmation state

Persistent business state holds:
- approved bike catalog
- official price
- confirmed booking
- booking status
- audit events

A lost conversation session must never erase an already confirmed booking.

## Fallback policy

1. First misunderstanding → clarification
2. Second misunderstanding → guided options
3. Third unresolved attempt → human handoff with context

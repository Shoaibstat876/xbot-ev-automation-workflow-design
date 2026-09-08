from app.enums import Intent
from app.services.intent_router import route_intent


def test_price_intent():
    assert route_intent("How much is this bike?").intent == Intent.PRICE_QUERY


def test_booking_intent():
    assert route_intent("I want to book a test ride").intent == Intent.BOOK_TEST_RIDE


def test_human_intent():
    assert route_intent("I want to speak to a person").intent == Intent.HUMAN_HANDOFF


def test_unknown_intent():
    assert route_intent("something unrelated").intent == Intent.UNKNOWN

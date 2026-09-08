from app.enums import Intent
from app.schemas import IntentResult


def route_intent(message: str) -> IntentResult:
    """
    Deterministic local fallback router for demo/testing.

    In production, this can be replaced by a structured-output LLM adapter.
    The backend must still validate all extracted entities and business actions.
    """
    text = message.strip().lower()

    if any(term in text for term in ["human", "agent", "support", "person"]):
        return IntentResult(intent=Intent.HUMAN_HANDOFF, confidence=0.95)

    if any(term in text for term in ["cancel", "stop", "never mind", "nevermind"]):
        return IntentResult(intent=Intent.CANCEL, confidence=0.95)

    if any(term in text for term in ["test ride", "test-ride", "ride", "book"]):
        return IntentResult(intent=Intent.BOOK_TEST_RIDE, confidence=0.85)

    if any(term in text for term in ["price", "cost", "how much"]):
        return IntentResult(intent=Intent.PRICE_QUERY, confidence=0.85)

    if any(term in text for term in ["help", "options", "menu"]):
        return IntentResult(intent=Intent.HELP, confidence=0.80)

    return IntentResult(intent=Intent.UNKNOWN, confidence=0.30)

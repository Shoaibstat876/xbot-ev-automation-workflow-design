from app.schemas import IntentResult


def classify_with_structured_output(message: str) -> IntentResult:
    """
    Placeholder adapter boundary for a future OpenAI Structured Outputs integration.

    The Task 3 source material proposes OpenAI for intent/entity extraction, but it does
    not provide a deployed API integration or credentials. This file intentionally
    defines the boundary without pretending the external integration already exists.
    """
    raise NotImplementedError(
        "Configure and implement the OpenAI structured-output adapter before enabling it."
    )

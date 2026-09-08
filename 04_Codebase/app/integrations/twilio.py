from twilio.request_validator import RequestValidator

from app.config import settings


def verify_twilio_signature(
    *,
    request_url: str,
    form_data: dict[str, str],
    signature: str | None,
) -> bool:
    """
    Verification is enforced only when TWILIO_AUTH_TOKEN is configured.
    """
    if not settings.twilio_auth_token:
        return settings.environment != "production"

    if not signature:
        return False

    validator = RequestValidator(settings.twilio_auth_token)
    return validator.validate(request_url, form_data, signature)

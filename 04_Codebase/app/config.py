from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "XBOT EV Task 3 Reference API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://xbot:xbot@localhost:5432/xbot_ev"

    twilio_auth_token: str | None = None
    twilio_whatsapp_number: str | None = None

    openai_api_key: str | None = None
    openai_model: str | None = None

    n8n_booking_webhook_url: str | None = None
    human_support_queue: str = "XBOT_EV_SUPPORT"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

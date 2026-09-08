from fastapi import FastAPI

from app.api.routes import router
from app.config import settings
from app.db import Base, engine
from app.logging_config import configure_logging


configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Reference backend scaffold for XBOT EV Task 3. "
        "This does not claim live production integrations."
    ),
)

# Suitable for the assessment scaffold.
# For production, replace create_all with migrations (e.g., Alembic).
Base.metadata.create_all(bind=engine)

app.include_router(router)

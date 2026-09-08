from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BikeModel


def list_active_models(db: Session) -> list[BikeModel]:
    return list(
        db.scalars(
            select(BikeModel)
            .where(BikeModel.is_active.is_(True))
            .order_by(BikeModel.model_name)
        )
    )


def get_model_by_code(db: Session, model_code: str) -> BikeModel | None:
    normalized = model_code.strip()
    return db.scalar(
        select(BikeModel).where(
            BikeModel.model_code.ilike(normalized),
            BikeModel.is_active.is_(True),
        )
    )

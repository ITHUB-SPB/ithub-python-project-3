from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models


def get_by_username(*, session: Session, username: str) -> models.User | None:
	query = select(models.User).where(models.User.username == username)
	return session.scalar(query)

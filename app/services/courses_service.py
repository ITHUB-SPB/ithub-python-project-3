from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import models


def get_list(
	*,
	session: Session,
) -> Sequence[models.Course]:
	return session.scalars(select(models.Course)).unique().all()

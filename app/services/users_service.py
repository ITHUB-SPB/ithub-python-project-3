from sqlalchemy import select
from sqlalchemy.orm import Session

from app import schema
from app.database import models
# from app.api import dependencies
# import OAuth2Form, CurrentUser, CursorDatabase, SessionDatabase


def get_by_username(*, session: Session, username: str) -> schema.UserResponse | None:
	"""
	:cursor: курсор подключения к базе данных
	:username: уникальный юзернейм пользователя

	Запрашивает пользователя из базы данных.
	Если пользователь не найден, возвращает None.
	Иначе - возвращает запись согласно схеме.
	"""

	user = session.scalar(select(models.User).where(models.User.username == username))

	if not user:
		return None

	return schema.UserResponse.model_validate(user)

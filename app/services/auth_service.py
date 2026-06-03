from sqlalchemy.orm import Session

from app import schema
from app.database import models
from app.security import create_access_token, get_password_hash, verify_password
from app.services import users_service


def register(*, session: Session, user_data: schema.UserCreate) -> models.User:
	user = models.User(
		username=user_data.username,
		password=get_password_hash(user_data.password),
	)
	session.add(user)
	session.commit()
	session.refresh(user)
	return user


def authenticate(*, session: Session, user_data: schema.UserCreate) -> str | None:
	user = users_service.get_by_username(session=session, username=user_data.username)
	if user is None:
		return None
	if not verify_password(user_data.password, user.password):
		return None
	return create_access_token(user.username)

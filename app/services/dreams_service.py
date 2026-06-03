import sqlite3
from collections.abc import Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import models
from app.database.exceptions import DuplicateDatabaseException


def get_by_id(session: Session, id: int) -> models.Dream | None:
	query = (
		select(models.Dream).options(joinedload(models.Dream.author)).where(models.Dream.id == id)
	)
	return session.scalar(query)


def get_list(
	*,
	session: Session,
	limit: int,
	offset: int,
	author: str | None = None,
) -> tuple[Sequence[models.Dream], int]:
	query = select(models.Dream).options(joinedload(models.Dream.author))
	count_query = select(func.count(models.Dream.id))
	if author:
		filter_clause = models.Dream.author_id.ilike(f'%{author}%')
		query = query.where(filter_clause)
		count_query = count_query.where(filter_clause)
	query = query.order_by(desc(models.Dream.id)).offset(offset).limit(limit)
	dreams = session.scalars(query).unique().all()
	dreams_count = session.scalar(count_query) or 0
	return dreams, dreams_count


def create(*, session: Session, new_dream: schema.NewDream, author_username: str) -> models.Dream:
	dream = models.Dream(description=new_dream.description, author_id=author_username)
	try:
		session.add(dream)
		session.commit()
		session.refresh(dream)
		return dream
	except (IntegrityError, sqlite3.IntegrityError) as exc:
		session.rollback()
		raise DuplicateDatabaseException from exc


def delete(*, session: Session, dream_id: int) -> None:
	dream = get_by_id(session, dream_id)
	if dream is None:
		return
	session.delete(dream)
	session.commit()

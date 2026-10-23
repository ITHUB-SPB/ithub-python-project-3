from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app import schema
from app.database import exceptions, models


def get_record_by_id(session: Session, id: int) -> models.Record | None:
	return (
		session.scalars(
			select(models.Record)
			.where(models.Record.id == id)
			.options(joinedload(models.Record.author).joinedload(models.Record.course))
		)
		.unique()
		.one_or_none()
	)


def get_records_list(
	*,
	session: Session,
	limit: int | None = 10,
	offset: int | None = 0,
	author: str | None = None,
	course: str | None = None,
) -> tuple[Sequence[models.Record], int]:
	expr = select(models.Record).options(
		joinedload(models.Record.author), joinedload(models.Record.course)
	)

	if author:
		expr = expr.where(models.Record.author.username == author)
	if course:
		expr = expr.where(models.Record.course.id == course)

	records = session.scalars(expr).all()
	paginated_records = session.scalars(expr.limit(limit).offset(offset)).unique().all()

	return paginated_records, len(records)


def create_record(*, session: Session, new_record: schema.RecordCreate) -> models.Record | None:
	record = models.Record(author_id=new_record.author_id, course_id=new_record.course_id)

	try:
		session.add(record)
		session.commit()
		session.refresh(record)
	except exceptions.DuplicateDatabaseException as e:
		raise e

	return session.scalar(
		select(models.Record)
		.where(models.Record.id == record.id)
		.options(joinedload(models.Record.course).joinedload(models.Record.author))
	)


def delete_record(*, session: Session, record_id: int) -> None:
	record_to_delete = (
		session.scalars(select(models.Record).where(models.Record.id == record_id))
		.unique()
		.one_or_none()
	)

	if not record_to_delete:
		raise exceptions.NotFoundDatabaseException

	session.execute(delete(models.Record).where(models.Record.id == record_id))

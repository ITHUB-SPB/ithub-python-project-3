from fastapi import APIRouter, Path, Query, status
from sqlalchemy import exc as dbExceptions

from app import schema
from app.api.dependencies import CurrentUser, SessionDatabase
from app.api.exceptions import (
	ConflictHTTPException,
	CredentialsHTTPException,
	NotAuthorizedHTTPException,
	NotFoundHTTPException,
)
from app.services import records_service

records_router = APIRouter(
	prefix='/records',
	tags=['Записи'],
)


@records_router.get(
	'/',
	summary='Список записей',
	description='Список записей с возможностью поиска, фильтрации, пагинации, с сортировкой по времени добавления',
	response_model=schema.RecordsListResponse,
	responses={
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Параметры запроса не валидные'}
	},
)
def get_records_list(
	session: SessionDatabase,
	limit: int = Query(20, title='Количество записей (по умолчанию 20)'),
	offset: int = Query(0, title='Величина отступа (по умолчанию  0)'),
	author: str = Query(None, title='Фильтр по юзернейму автора'),
	course: str = Query(None, title='Фильтр по курсу'),
) -> schema.RecordsListResponse:
	return records_service.get_records_list(
		session=session, limit=limit, offset=offset, course=course, author=author
	)


@records_router.post(
	'/',
	summary='Добавление записи',
	description='Добавление записи (требуется авторизация)',
	response_model=schema.RecordResponse,
	status_code=201,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_409_CONFLICT: {'description': 'Пользователь уже добавлял запись на этот курс'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Данные не валидны'},
	},
)
def create_record(
	current_user: CurrentUser,
	session: SessionDatabase,
	new_record_payload: schema.RecordCreate,
) -> schema.RecordResponse:
	print(current_user)
	if not current_user:
		raise CredentialsHTTPException

	try:
		new_record = records_service.create_record(
			session=session, author_id=current_user.username, course_id=new_record_payload.course_id
		)
		return schema.RecordResponse.model_validate(new_record)
	except dbExceptions.IntegrityError:
		raise ConflictHTTPException


@records_router.get(
	'/{id}',
	summary='Чтение записи',
	response_model=schema.RecordResponse,
	responses={
		status.HTTP_404_NOT_FOUND: {'description': 'Запись не найдена'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def get_record(
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор записи для чтения'),
) -> schema.RecordResponse:
	record = records_service.get_record_by_id(session=session, id=id)

	if not record:
		raise NotFoundHTTPException

	return schema.RecordResponse.model_validate(record)


@records_router.delete(
	'/{id}',
	summary='Удаление сна',
	description='Удаление сна (требуется авторизация для удаления собственных снов',
	status_code=204,
	responses={
		status.HTTP_401_UNAUTHORIZED: {'description': 'Ошибка токена или пользовательских данных'},
		status.HTTP_404_NOT_FOUND: {'description': 'Запись не найдена'},
		status.HTTP_403_FORBIDDEN: {'description': 'Пользователь не является автором записи'},
		status.HTTP_422_UNPROCESSABLE_CONTENT: {'description': 'Идентификатор не валиден'},
	},
)
def delete_record(
	current_user: CurrentUser,
	session: SessionDatabase,
	id: int = Path(..., title='Идентификатор записи для удаления'),
) -> None:
	if not current_user:
		raise CredentialsHTTPException

	record_to_delete = records_service.get_record_by_id(session=session, id=id)

	if not record_to_delete:
		raise NotFoundHTTPException

	if not record_to_delete.author_id == current_user.username:
		raise NotAuthorizedHTTPException

	records_service.delete_record(session=session, record_id=id)

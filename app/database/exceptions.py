from sqlalchemy import exc


class DuplicateDatabaseException(exc.IntegrityError):
	def __init__(self, message: str | None = 'Запись уже существует'):
		super().__init__(message, params=None)


class NotFoundDatabaseException(exc.NoResultFound):
	def __init__(self, message: str | None = 'Запись не найдена'):
		super().__init__(message)

import os
import secrets
import typing

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_database_uri() -> str:
	if os.getenv('PYTHON_ENVIRONMENT') == 'testing':
		return 'sqlite:///./app/database/testing.sqlite3'
	return 'sqlite:///./app/database/local.sqlite3'


def get_env_file() -> str:
	if os.getenv('PYTHON_ENVIRONMENT') == 'testing':
		return '.env.testing'
	return '.env.local'


class Settings(BaseSettings):
	DEBUG: bool = os.getenv('PYTHON_ENVIRONMENT') != 'testing'
	JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
	JWT_EXPIRE: int = 60 * 24 * 8
	JWT_ALGORITHM: typing.Literal['HS256'] = 'HS256'
	PASSWORD_SALT: bytes = secrets.token_bytes(32)
	DATABASE_URI: str = get_database_uri()

	model_config = SettingsConfigDict(
		env_file=get_env_file(),
		extra='ignore',
	)

	@field_validator('DEBUG', mode='before')
	@classmethod
	def validate_debug(cls, value: object) -> object:
		if isinstance(value, str):
			lower_value = value.lower()
			if lower_value in {'1', 'true', 'yes', 'on'}:
				return True
			if lower_value in {'0', 'false', 'no', 'off', 'release'}:
				return False
		return value


settings = Settings()

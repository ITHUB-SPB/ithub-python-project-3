from fastapi import FastAPI

from app.api import api_auth, api_courses, api_records
from app.config import settings

app = FastAPI(debug=settings.DEBUG, title='InDreams', description='InDreams API')

app.include_router(api_records.records_router)
app.include_router(api_auth.auth_router)
app.include_router(api_courses.courses_router)

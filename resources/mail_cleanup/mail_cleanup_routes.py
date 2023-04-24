from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from fastapi import APIRouter, Depends, UploadFile
from resources.mail_cleanup.mail_cleanup_use_cases import MailCleanupUseCases

mail_cleanup_router = APIRouter(
    prefix="/mail_cleanup"
)


@mail_cleanup_router.post("")
async def get_users_active(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list:
    file_binary = await file.read()
    return await MailCleanupUseCases.cleanup_by_phones(file_binary=file_binary, async_session=async_session)

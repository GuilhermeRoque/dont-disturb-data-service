import dataclasses

from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from fastapi import APIRouter, Depends, UploadFile
from resources.import_routines.import_routines_use_case import MailCleanupUseCases, ImportReportUpdated
from resources.phones.phone import PhoneRegistered

mail_cleanup_router = APIRouter(
    prefix="/import-routines"
)


@mail_cleanup_router.post("/cleanup")
async def cleanup(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list[ImportReportUpdated]:
    file_binary = await file.read()
    return await MailCleanupUseCases.cleanup_by_phones(file_binary=file_binary, async_session=async_session)


@mail_cleanup_router.post("/update")
async def update_phones(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list[ImportReportUpdated]:
    file_binary = await file.read()
    return await MailCleanupUseCases.update_by_phones(file_binary=file_binary, async_session=async_session)

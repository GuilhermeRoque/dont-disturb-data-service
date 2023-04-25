from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from fastapi import APIRouter, Depends, UploadFile
from resources.import_routines.import_phones_use_case import ImportPhonesUseCases, ImportReportUpdated
from resources.import_routines.import_users_use_case import ImportUsersUseCase
from resources.users.user import UserRegistered

mail_cleanup_router = APIRouter(
    prefix="/import-routines"
)

@mail_cleanup_router.get("")
async def caralho( async_session: AsyncSession = Depends(get_db_conn)):
    return {"OLA":"OLA"}
@mail_cleanup_router.post("/cleanup-phones")
async def cleanup(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list[ImportReportUpdated]:
    file_binary = await file.read()
    return await ImportPhonesUseCases.cleanup_by_phones(file_binary=file_binary, async_session=async_session)


@mail_cleanup_router.post("/phones")
async def update_phones(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list[ImportReportUpdated]:
    file_binary = await file.read()
    return await ImportPhonesUseCases.update_by_phones(file_binary=file_binary, async_session=async_session)


@mail_cleanup_router.post("/users")
async def create_users(file: UploadFile, async_session: AsyncSession = Depends(get_db_conn)) -> list[UserRegistered]:
    file_binary = await file.read()
    return await ImportUsersUseCase.crate_users_import(file_binary=file_binary, async_session=async_session)

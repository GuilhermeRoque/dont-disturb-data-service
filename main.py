from dotenv import load_dotenv; load_dotenv()

from starlette.responses import JSONResponse
import http
import traceback
from resources.utils.use_cases_execeptions import UseCasesExceptions
from fastapi import Request
from logger import default_logger
import uvicorn
from resources.users_active.user_active_routes import user_active_router
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from resources.users.user_routes import user_router
from db import async_engine
from alembic import command, config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(user_router)
app.include_router(user_active_router)


@app.exception_handler(UseCasesExceptions)
async def handle_use_case_exception(request: Request, e: UseCasesExceptions):
    return JSONResponse(
        status_code=e.get_error_code(),
        content={"message": e.get_message()},
    )


@app.exception_handler(Exception)
async def handle_use_case_exception(request: Request, e: Exception):
    return JSONResponse(
        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"},
    )


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@app.on_event("startup")
async def run_async_upgrade():
    default_logger.info("Running migrations...")
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config.Config("alembic.ini"))
    default_logger.info("Finish running migrations!")


@app.get("/echo")
async def echo():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", access_log=True)

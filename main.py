from dotenv import load_dotenv; load_dotenv()
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


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@app.on_event("startup")
async def run_async_upgrade():
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config.Config("alembic.ini"))


@app.get("/echo")
async def echo():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", access_log=True)

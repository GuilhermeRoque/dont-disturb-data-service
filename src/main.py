from dotenv import load_dotenv; load_dotenv()
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from resources.users.user_routes import user_router
from db import async_engine, Base
import uvicorn

app = FastAPI()
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info", access_log=True)

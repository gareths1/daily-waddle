"""FastAPI entrypoint.  Run:  uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.routers import penguins
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as session:
        await seed_if_empty(session)  # API works out of the box
    yield


app = FastAPI(
    title="The Daily Waddle",
    description="A public, read-only penguin API.",
    version="1.0.0",
    lifespan=lifespan,
)

# Read-only public API: allow GET only, no credentials/cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["GET"],
    allow_headers=[],
    allow_credentials=False,
)

app.include_router(penguins.router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}

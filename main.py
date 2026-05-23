import uvicorn

from fastapi import FastAPI
from contextlib import asynccontextmanager

from database.db import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Database is ready")

    yield

    print("Shutting down server")

app = FastAPI(
    lifespan=lifespan,
    title="Home Library API",
    description="A simple API for managing your home library",
    version="1.0.0"
)


if __name__ == "__main__":
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

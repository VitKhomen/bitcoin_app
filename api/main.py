from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from database.engine import create_tables
from api.routers import users, wallets, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск: створюємо таблиці (для розробки, в продакшені — alembic)
    await create_tables()
    print("✅ Database ready")
    yield
    print("🛑 Shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="Bitcoin Wallet API",
    description="API для Bitcoin-гаманців з Telegram ботом",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(wallets.router)
app.include_router(transactions.router)


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

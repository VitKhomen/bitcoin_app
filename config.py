from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/bitcoin_wallet"

    # Telegram
    BOT_TOKEN: str = ""

    # Bitcoin
    TESTNET: bool = True  # False для mainnet

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

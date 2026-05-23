
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


# ====================== USER ======================

class UserBase(BaseModel):
    tg_ID: int
    nick: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    create_date: datetime
    wallet: Optional["WalletRead"] = None  # для вкладеного відображення

    model_config = ConfigDict(from_attributes=True)


# ====================== WALLET ======================

class WalletBase(BaseModel):
    address: str
    balance: float = Field(default=0.0, ge=0)


class WalletCreate(BaseModel):
    """Використовується при створенні гаманця"""
    private_key: str
    address: str


class WalletRead(WalletBase):
    id: int
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ====================== TRANSACTION ======================

class TransactionBase(BaseModel):
    amount_btc_with_fee: float = Field(gt=0)
    amount_btc_without_fee: float = Field(gt=0)
    fee: float = Field(ge=0)
    sender_address: Optional[str] = None
    receiver_address: str


class TransactionCreate(BaseModel):
    """Схема для створення транзакції"""
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    sender_wallet_id: Optional[int] = None
    receiver_wallet_id: Optional[int] = None
    sender_address: Optional[str] = None
    receiver_address: str
    amount_btc_with_fee: float
    amount_btc_without_fee: float
    fee: float
    tx_hash: str


class TransactionRead(TransactionBase):
    id: int
    date_of_transaction: datetime
    tx_hash: str
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    sender_wallet_id: Optional[int] = None
    receiver_wallet_id: Optional[int] = None

    sender: Optional["UserRead"] = None
    receiver: Optional["UserRead"] = None
    sender_wallet: Optional["WalletRead"] = None
    receiver_wallet: Optional["WalletRead"] = None

    model_config = ConfigDict(from_attributes=True)


# ====================== RESPONSE SCHEMAS ======================

class UserWithWallet(UserRead):
    wallet: Optional[WalletRead] = None


class TransactionList(BaseModel):
    items: List[TransactionRead]
    total: int


# Для вирішення forward references
UserRead.model_rebuild()
TransactionRead.model_rebuild()
UserWithWallet.model_rebuild()

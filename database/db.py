from datetime import datetime
from typing import Optional, list

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    tg_ID: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    nick: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # One-to-One з Wallet
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    sended_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
        lazy="selectin"
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
        lazy="selectin"
    )


class Wallet(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('users.id'), unique=True, nullable=True
    )

    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    private_key: Mapped[str] = mapped_column(
        String, unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="wallet")

    sended_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_wallet_id",
        back_populates="sender_wallet",
        lazy="selectin"
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_wallet_id",
        back_populates="receiver_wallet",
        lazy="selectin"
    )


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    sender_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=True
    )
    receiver_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=True
    )

    sender_wallet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('wallets.id'), nullable=True
    )
    receiver_wallet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('wallets.id'), nullable=True
    )

    sender_address: Mapped[Optional[str]
                           ] = mapped_column(String, nullable=True)
    receiver_address: Mapped[Optional[str]
                             ] = mapped_column(String, nullable=True)

    amount_btc_with_fee: Mapped[float] = mapped_column(Float, nullable=False)
    amount_btc_without_fee: Mapped[float] = mapped_column(
        Float, nullable=False)
    fee: Mapped[float] = mapped_column(Float, nullable=False)

    date_of_transaction: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    tx_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationships
    sender: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sended_transactions"
    )

    receiver: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_transactions"
    )

    sender_wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet",
        foreign_keys=[sender_wallet_id],
        back_populates="sended_transactions"
    )

    receiver_wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet",
        foreign_keys=[receiver_wallet_id],
        back_populates="received_transactions"
    )

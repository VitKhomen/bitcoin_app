from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.engine import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, index=True)
    nick: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # One-to-One: у кожного юзера один кошелек
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",  # автоматично підвантажується разом з юзером
    )

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_id",
        back_populates="sender",
        lazy="selectin",
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_id",
        back_populates="receiver",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg_id={self.tg_id} nick={self.nick}>"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True
    )
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    private_key: Mapped[str] = mapped_column(
        String, unique=True, nullable=False)
    address: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)

    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="wallet")

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.sender_wallet_id",
        back_populates="sender_wallet",
        lazy="selectin",
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.receiver_wallet_id",
        back_populates="receiver_wallet",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Wallet id={self.id} address={self.address} balance={self.balance}>"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)

    sender_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    receiver_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    sender_wallet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True
    )
    receiver_wallet_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True
    )

    sender_address: Mapped[Optional[str]
                           ] = mapped_column(String, nullable=True)
    receiver_address: Mapped[str] = mapped_column(String, nullable=False)

    # Суми в сатоші (int надійніший за float для грошей)
    amount_satoshi: Mapped[int] = mapped_column(Integer, nullable=False)
    fee_satoshi: Mapped[int] = mapped_column(Integer, nullable=False)

    date_of_transaction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    tx_hash: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True)

    # Relationships
    sender: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_transactions"
    )
    receiver: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_transactions"
    )
    sender_wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet", foreign_keys=[sender_wallet_id], back_populates="sent_transactions"
    )
    receiver_wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet", foreign_keys=[receiver_wallet_id], back_populates="received_transactions"
    )

    @property
    def amount_btc(self) -> float:
        """Конвертуємо сатоші в BTC для відображення."""
        return self.amount_satoshi / 100_000_000

    @property
    def fee_btc(self) -> float:
        return self.fee_satoshi / 100_000_000

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} amount={self.amount_satoshi} sat hash={self.tx_hash[:8]}...>"

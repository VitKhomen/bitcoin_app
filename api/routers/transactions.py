from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Transaction, User
from schemas.transaction import TransactionCreate
from services import bitcoin


async def create_transaction(
    db: AsyncSession,
    data: TransactionCreate,
    sender: User,
) -> Transaction:
    """
    Відправляє Bitcoin-транзакцію і зберігає запис в БД.
    Кидає ValueError якщо баланс недостатній.
    """
    wallet = sender.wallet
    fee = data.fee_satoshi or bitcoin.estimate_fee()

    # Відправляємо через bitcoin service — якщо не вистачить балансу, кине ValueError
    result = bitcoin.send_transaction(
        private_key_wif=wallet.private_key,
        receiver_address=data.receiver_address,
        amount_satoshi=data.amount_satoshi,
        fee_satoshi=fee,
    )

    # Шукаємо чи є receiver в нашій БД (необов'язково)
    receiver_wallet_result = await db.execute(
        select(User).join(User.wallet).where(
            User.wallet.has(address=data.receiver_address)
        )
    )
    receiver = receiver_wallet_result.scalar_one_or_none()

    transaction = Transaction(
        sender_id=sender.id,
        receiver_id=receiver.id if receiver else None,
        sender_wallet_id=wallet.id,
        receiver_wallet_id=receiver.wallet.id if receiver else None,
        sender_address=wallet.address,
        receiver_address=data.receiver_address,
        amount_satoshi=result.amount_satoshi,
        fee_satoshi=result.fee_satoshi,
        date_of_transaction=datetime.now(timezone.utc),
        tx_hash=result.tx_hash,
    )
    db.add(transaction)

    # Оновлюємо баланс відправника (спрощено — знімаємо локально без запиту в мережу)
    total_spent_btc = (result.amount_satoshi +
                       result.fee_satoshi) / 100_000_000
    wallet.balance = max(0.0, wallet.balance - total_spent_btc)

    await db.flush()
    return transaction


async def get_transaction_by_hash(db: AsyncSession, tx_hash: str) -> Transaction | None:
    result = await db.execute(
        select(Transaction).where(Transaction.tx_hash == tx_hash)
    )
    return result.scalar_one_or_none()


async def get_user_transactions(db: AsyncSession, user_id: int) -> list[Transaction]:
    result = await db.execute(
        select(Transaction).where(
            (Transaction.sender_id == user_id) | (
                Transaction.receiver_id == user_id)
        ).order_by(Transaction.date_of_transaction.desc())
    )
    return list(result.scalars().all())

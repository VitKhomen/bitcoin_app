"""
services/bitcoin.py

Вся логіка роботи з Bitcoin винесена сюди.
Решта коду (crud, handlers) не знає нічого про bitcoinlib — тільки викликає ці функції.
"""
from dataclasses import dataclass

from bitcoinlib.wallets import Wallet as BtcWallet
from bitcoinlib.keys import Key

from config import settings


NETWORK = "testnet" if settings.TESTNET else "bitcoin"


@dataclass
class NewWalletData:
    address: str
    private_key: str  # WIF формат


@dataclass
class TransactionResult:
    tx_hash: str
    fee_satoshi: int
    amount_satoshi: int


def create_new_wallet() -> NewWalletData:
    """Генеруємо нову пару ключів (адреса + приватний ключ)."""
    key = Key(network=NETWORK)
    return NewWalletData(
        address=key.address(),
        private_key=key.wif(),
    )


def import_wallet(private_key_wif: str) -> NewWalletData:
    """Імпортуємо існуючий кошелек за приватним ключем."""
    key = Key(import_key=private_key_wif, network=NETWORK)
    return NewWalletData(
        address=key.address(),
        private_key=key.wif(),
    )


def get_balance(address: str) -> int:
    """Повертає баланс в сатоші."""
    # bitcoinlib може отримати баланс через публічний API
    wallet = BtcWallet.create(
        name=f"tmp_{address[:8]}",
        keys=address,
        network=NETWORK,
        witness_type="segwit",
        db_uri=":memory:",  # тимчасовий in-memory, не зберігаємо
    )
    wallet.scan()
    balance = wallet.balance()
    wallet.delete_wallet(wallet.name)
    return balance


def estimate_fee(num_outputs: int = 1) -> int:
    """
    Проста оцінка комісії: ~250 байт транзакція, 20 sat/byte для testnet.
    В продакшені варто брати актуальний fee rate з API.
    """
    fee_rate = 20  # sat/byte
    tx_size_bytes = 150 + 50 * num_outputs
    return fee_rate * tx_size_bytes


def send_transaction(
    private_key_wif: str,
    receiver_address: str,
    amount_satoshi: int,
    fee_satoshi: int,
) -> TransactionResult:
    """
    Відправляє транзакцію і повертає хеш.
    Кидає ValueError якщо баланс недостатній.
    """
    wallet = BtcWallet.create(
        name=f"sender_{private_key_wif[:8]}",
        keys=private_key_wif,
        network=NETWORK,
        witness_type="segwit",
        db_uri=":memory:",
    )
    wallet.scan()

    balance = wallet.balance()
    total_needed = amount_satoshi + fee_satoshi

    if balance < total_needed:
        raise ValueError(
            f"Недостатньо коштів. Баланс: {balance} sat, потрібно: {total_needed} sat"
        )

    tx = wallet.send_to(
        to_address=receiver_address,
        amount=amount_satoshi,
        fee=fee_satoshi,
        broadcast=True,
    )

    wallet.delete_wallet(wallet.name)

    return TransactionResult(
        tx_hash=tx.txid,
        fee_satoshi=fee_satoshi,
        amount_satoshi=amount_satoshi,
    )

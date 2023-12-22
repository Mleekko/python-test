import asyncio
import os
from datetime import datetime, timezone, timedelta
import time
from typing import Tuple
from radix_engine_toolkit import *


# account common
def derive_account(private_key_bytes: bytes, network_id: int) -> Tuple[PrivateKey, Address]:
    private_key: PrivateKey = PrivateKey.new_ed25519(private_key_bytes)
    public_key: PublicKey = private_key.public_key()
    account: Address = derive_virtual_account_address_from_public_key(
        public_key, network_id
    )
    return private_key, account


# Nonce
NONCE: int = 0
NONCE_FILE = './nonce.txt'


def read_nonce():
    global NONCE
    if os.path.isfile(NONCE_FILE):
        with open(NONCE_FILE, 'r') as f:
            NONCE = int(f.read().strip())


async def save_nonce(n):
    with open(NONCE_FILE, 'w') as f:
        f.write(str(n))


def next_nonce() -> int:
    global NONCE
    NONCE = NONCE + 1

    asyncio.create_task(save_nonce(NONCE))
    return NONCE


read_nonce()


# Other
def sleep_until(target):
    now = datetime.now(timezone.utc)
    delta = target - now

    if delta > timedelta(0):
        print(f"Sleeping for: {delta.total_seconds()} seconds...\n")
        time.sleep(delta.total_seconds())
        return True


import os

from radix_engine_toolkit import *
from typing import Tuple
import secrets

KEY_FILE = './private-key.txt'
NETWORK_ID: int = OlympiaNetwork.MAINNET.value


def derive_account(private_key_bytes: bytes, network_id: int) -> Tuple[PrivateKey, Address]:
    private_key: PrivateKey = PrivateKey.new_ed25519(private_key_bytes)
    public_key: PublicKey = private_key.public_key()
    account: Address = derive_virtual_account_address_from_public_key(
        public_key, network_id
    )
    return private_key, account


if not os.path.isfile(KEY_FILE):
    private_key_bytes: bytes = secrets.randbits(256).to_bytes(32)
    (_, account) = derive_account(private_key_bytes, NETWORK_ID)
    with open(KEY_FILE, 'w') as f:
        raw_key: str = private_key_bytes.hex()
        f.write(raw_key)
        print(f"Generated a new private key.\nYour account is: {account.address_string()}\n")
    exit(0)
else:
    with open(KEY_FILE, 'r') as f:
        raw_key = f.read().strip()
    private_key_bytes: bytes = bytes.fromhex(raw_key)
    (_, account) = derive_account(private_key_bytes, NETWORK_ID)
    print(f"'{KEY_FILE}' already exists.\nYour account is: {account.address_string()}\n"
          f"Skipped creating a new private key.\n")
    exit(0)







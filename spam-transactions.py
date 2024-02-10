from client.gateway_client import GatewayClient
from common import *

# Modify params here
START_TIME = '2023-12-22T15:15:00.000Z'
KEY_FILE = './private-key.txt'
TARGET_ACCOUNT: Address = Address('account_tdx_2_129teakwy0m2e2rn33krkd6phh4aauy347hsyc05ljdq5yvemaz6s5w')
NETWORK_ID: int = OlympiaNetwork.STOKENET.value
GATEWAY_URL = 'https://stokenet-gateway.radix.live/'
#
# START_TIME = '2023-12-15T18:25:00.000Z'
# KEY_FILE = './private-key.txt'
# TARGET_ACCOUNT: Address = Address('account_rdx12x77n5xde8sf8xmw0cz9un547wj4t42m946u48qt998n3heset652x')
# NETWORK_ID: int = OlympiaNetwork.MAINNET.value
# GATEWAY_URL = 'https://gateway.radix.live/'
#

with open(KEY_FILE, 'r') as f:
    raw_key = f.read().strip()
private_key_bytes: bytes = bytes.fromhex(raw_key)
(private_key, account) = derive_account(private_key_bytes, NETWORK_ID)
public_key = private_key.public_key()
print(f"Your account is: {account.address_string()}\n")

address_book: KnownAddresses = known_addresses(NETWORK_ID)
faucet_address: Address = address_book.component_addresses.faucet
xrd_address: Address = address_book.resource_addresses.xrd


def build_transaction(epoch: int, nonce: int) -> NotarizedTransaction:
    """
        Builds a transaction to transfer 0.01 XRD to the `TARGET_ACCOUNT` and signs it with the private key
    """
    manifest: TransactionManifest = (
        ManifestBuilder()
        .account_lock_fee(account, Decimal("1"))
        .account_withdraw(account, xrd_address, Decimal("0.01"))
        .take_from_worktop(xrd_address, Decimal("0.01"), ManifestBuilderBucket("bucket1"))
        .account_try_deposit_or_abort(TARGET_ACCOUNT, ManifestBuilderBucket("bucket1"), None)
        .build(NETWORK_ID)
    )

    header: TransactionHeader = TransactionHeader(
        network_id=NETWORK_ID,
        start_epoch_inclusive=epoch,
        end_epoch_exclusive=epoch + 5,
        nonce=nonce,
        notary_public_key=public_key,
        notary_is_signatory=True,
        tip_percentage=0,
    )

    return (TransactionBuilder()
            .header(header)
            .manifest(manifest)
            .sign_with_private_key(private_key)
            .notarize_with_private_key(private_key))


async def main():
    """
        Entry point
    """
    start_time = datetime.fromisoformat(START_TIME)
    sleep_until(start_time)

    client = GatewayClient(GATEWAY_URL)

    epoch: int = await client.get_current_epoch()
    print(f"Epoch: {epoch}\n")

    for i in range(500):
        duplicate: bool = True
        while duplicate:
            transaction: NotarizedTransaction = build_transaction(epoch, next_nonce())
            tx_bytes: bytes = transaction.compile()
            duplicate = await client.submit_transaction(tx_bytes.hex())


asyncio.run(main())

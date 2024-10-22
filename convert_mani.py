from radix_engine_toolkit import *
from common import *

NETWORK_ID: int = OlympiaNetwork.MAINNET.value

address_book: KnownAddresses = known_addresses(NETWORK_ID)
faucet_address: Address = address_book.component_addresses.faucet
xrd_address: Address = address_book.resource_addresses.xrd

manifest: TransactionManifest = (
    ManifestBuilder()
    .faucet_lock_fee()
    .faucet_free_xrd()
    .take_from_worktop(xrd_address, Decimal("5000"), ManifestBuilderBucket("bucket1"))
    .take_from_worktop(xrd_address, Decimal("5000"), ManifestBuilderBucket("bucket2"))
    .account_deposit(Address("account_rdx168gnr2atp6tzvljeuc407596cgnszk9ngddzk9u3af6krhjwxwatch"),
                     ManifestBuilderBucket("bucket1"))
    .account_deposit(Address("account_rdx16998xell0000000000000000000000000000000000000000000000"),
                     ManifestBuilderBucket("bucket2"))
    .build(NETWORK_ID)
)



print(f"Manifest as string (remember to delete `lock_fee`!):\n{manifest.instructions().as_str()}\n")


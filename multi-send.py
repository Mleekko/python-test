from client.gateway_client import GatewayClient
from common import *
from radix_engine_toolkit import *

# Modify params here
KEY_FILE = './private-key.txt'
NETWORK_ID: int = OlympiaNetwork.MAINNET.value
GATEWAY_URL = 'https://gateway.radix.live/'
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

rec = """
account_rdx169mvxzd8am44empgl5xr8lqvkplwch2tl3uzsec0mrtktld0malcka
account_rdx1692eahlxp2jk86p55kst8rdcc7zkdq8zgzkh28n7rw56728pzjdrgs
account_rdx129z9cxpxzxqmftprd5wjmj28c2f2g0t9lguaw3qs7xpk8sth72rarm
account_rdx168xxqs0nw8k7gmfhrvc9weuj9clcsjhw4npqj7vcv735mznldr9mzg
account_rdx16ys9ftp4slu39pyjl6dq62dgk6eayvd38c9gfsxmp0pwmr5mcs28qp
account_rdx168kl835vkkd7gqzlv8ayy385xte5lpae06qa0ylwu3d2fqvuk0xpmy
account_rdx16x0s44zry5hn9hacquzxjwjfy5dvevklrmdu48hcjvylun3g3mm58q
account_rdx169t5kaft6hae9j07qqnfgmlnpgneu0508hpx000azr6pl67sjde0qn
account_rdx169ch72gu5m3zh3v0wa9fx6prcu946hxhfkx3k6xhq2z0j5cd2pnzhp
account_rdx1290cuuyzxjmrdulxqvfqv3qnh4n6s33rh350afgthc6wq27ynucra0
account_rdx16ynf0tn69hhmjtc4w0ek5tvguu2f9re6qtcg0msgf03y43aw2m0lq5
account_rdx16837uslm2dvrya42gp9ymxspr9qfqgvtn5jjhmf8r7pm806rwv8r34
account_rdx16ymkqcd53azhr36k20g87s6feddm6zzd9ghqkuh0wpdmakuyjgnfun
account_rdx169dg0fcpzlt2797z5p2xa90lql3e4zjc63f4j93vq3g0fnmwecj6m3
account_rdx129cpudkgjvkpkqnmz8drengdn5y89crhdq9mskfc7xcgum83rnfhh2
account_rdx128fg43hwdmanhuxjm7qpp9gf4x8yv4jgn7crnndnvrffcg3e22gwpr
account_rdx16876r38y5vhqlrugqt4wt5shrxtc0nfxpx69g78z9f3g40tda90qme
account_rdx16y2ntansfl5xjfr66j8ymcjrf7cq8eu0j69gkstm9r5g2xmkz8wz69
account_rdx1684xfheqgvw9fhk6sftscrsxc6e8fk8h2l6y59hfyxtqqld6f546a7
account_rdx16yuwzgn6mau03rdag0nrxndv9je4u3y87p9fge96g5a63m3qjea574
account_rdx16xne7wxp40c868jwh7kqm0nk7rur7tx9epw3hjrtscsslhvt6tq3rj
account_rdx1290e4yz2vuvavgxj2c6tvnanrtyalgtd6sh7crehm20tzckdvsd22t
account_rdx168030sml62xd68ltwnhz8qe2qzd9guw6nglzz68exxelvq68medzrd
account_rdx16952myqm6rs2hku9jkwtp6gtrxr03e2knvf2980k5pk0tmvjhue6m7
account_rdx16y5aujpfk236ed0gpnme3k02vgyxwx5tx9wym8hdhunjkeqsl4a3va
account_rdx1289kp3wan60npgfxckepzkmwgwu7d83p5pldl8xcnw3f954f706jt2
account_rdx16xfrgh0l0aamm3se0arh0u4srdvhz8q3vk70pxsak4rkjgzq4lwfwc
account_rdx129844r05eyk8467874l5v3cpww6v2plsxscm62c00zwhlvknllzvcw
account_rdx16x5l69u3cpuy59g8n0g7xpv3u3dfmxcgvj8t7y2ukvkjn8pjz2v492
account_rdx12x480eadq6eyxwcexej8hvtshvxjss8mlv7lgygw5ucj88xyah64lp
account_rdx169pqxzscglwtaz0uz3urtk5d806rf6rsa4ujwmfty0hurhv03sxkkp
account_rdx16xk9468emvt6q9svt7d9xcx9tdtz43ycygqu3nwd3xdhzuyhh0ngaf
account_rdx1284v7ugctp0u7u2cefraep89xa3njga44dguh5l9qjt0vg5nevrjpc
account_rdx1286q6llw7wfa5hlq3rdkt2hvl3lluxrcly3kh3nxc84r09rszlpea5
account_rdx128dmck057t6mzr26tw9l8r2xkm8mdxslvt4y4jl58wmzhzdc5nsxj6
account_rdx128ku70k3nxy9q0ekcwtwucdwm5jt80xsmxnqm5pfqj2dyjswgh3rm3
account_rdx128ldshjmrge7j98ydag7qgsdk2t79qqlxpw5j2warzqnju7mg6x605
account_rdx128m799c5dketq0v07kqukamuxy6zfca0vqttyjj5av6gcdhlkwpy2r
account_rdx128n7w9ph7qq5j6dvd3lzf00v052xsux4797dmd8ag3j327n5d54l5t
account_rdx128p673ffeg8knc3et8m35vde9p9u9ltu4dpx72tserxmz8jynllf3a

"""

RECIPIENTS = []
for line in rec.splitlines():
    if len(line.strip()) > 10:
        RECIPIENTS.append(line.strip())


MESSAGE = ("There is Water (ICE) in your account. Please join the Random mint event!"
           " \nDetails: https://t.me/WaterXRD/3669\nhttps://ice-randomizer-dapp.pages.dev")


def build_transaction(recipients: [str], epoch: int, nonce: int) -> NotarizedTransaction:
    builder = (ManifestBuilder()
               .account_lock_fee(account, Decimal("10"))
               .account_withdraw(account, xrd_address, Decimal(str(0.1 * len(recipients)))))
    for (i, recipient) in enumerate(recipients):  # type: (int, str)
        builder = (builder.take_from_worktop(xrd_address, Decimal("0.1"), ManifestBuilderBucket(f"bucket{i}"))
                   .account_try_deposit_or_refund(Address(recipient), ManifestBuilderBucket(f"bucket{i}"), None)
        )
    manifest: TransactionManifest = builder.account_deposit_entire_worktop(account).build(NETWORK_ID)

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
            .message(Message.PLAIN_TEXT(PlainTextMessage("text/plain", MessageContent.STR(MESSAGE))))
            .sign_with_private_key(private_key)
            .notarize_with_private_key(private_key))


async def main():
    """
        Entry point
    """
    client = GatewayClient(GATEWAY_URL)

    epoch: int = await client.get_current_epoch()
    print(f"Epoch: {epoch}\n")

    duplicate: bool = True
    while duplicate:
        transaction: NotarizedTransaction = build_transaction(RECIPIENTS, epoch, next_nonce())
        tx_bytes: bytes = transaction.compile()
        duplicate = await client.submit_transaction(tx_bytes.hex())
        print(f"Sent Transaction: {transaction.intent_hash().as_str()}\n")


asyncio.run(main())

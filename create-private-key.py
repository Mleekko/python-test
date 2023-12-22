from common import *
import qrcode
import secrets

KEY_FILE = './private-key.txt'
NETWORK_ID: int = OlympiaNetwork.MAINNET.value

if not os.path.isfile(KEY_FILE):
    private_key_bytes: bytes = secrets.randbits(256).to_bytes(32)
    (_, account) = derive_account(private_key_bytes, NETWORK_ID)
    with open(KEY_FILE, 'w') as f:
        raw_key: str = private_key_bytes.hex()
        f.write(raw_key)
        print(f"Generated a new private key.\nYour account is: {account.address_string()}\n")
else:
    with open(KEY_FILE, 'r') as f:
        raw_key = f.read().strip()
    private_key_bytes: bytes = bytes.fromhex(raw_key)
    (_, account) = derive_account(private_key_bytes, NETWORK_ID)
    print(f"'{KEY_FILE}' already exists.\nSkipped creating a new private key.\n\n"
          f"Your account is: {account.address_string()}\n")

qr = qrcode.QRCode()
qr.add_data(account.address_string())
qr.print_ascii()







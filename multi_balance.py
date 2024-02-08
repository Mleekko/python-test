import decimal
from typing import Dict

from astro_client import AstroClient
from common import *
from decimal import *


from gateway_client import GatewayClient
from caviar_client import CaviarClient

NETWORK_ID: int = OlympiaNetwork.MAINNET.value

KEY_FILE = './all-wallets.txt'

all_wallets = []

with open(KEY_FILE, 'r') as f:
    for full_line in f.readlines():
        line = full_line.strip()
        if len(line) > 0:
            all_wallets.append(line)


def pad(s: str, i: int) -> str:
    if len(s) >= i:
        return s

    return s + " " * (i - len(s))


def disp(num: decimal.Decimal) -> str:
    return format(num, ',')


def precision(num: decimal.Decimal, n=1) -> decimal.Decimal:
    order = num.log10().__floor__()
    prec = n - order - 1
    power = decimal.Decimal(10.0 ** prec)
    res = decimal.Decimal((num * power).__round__() / power)
    return res if prec > 0 else res.__round__()


class TokenValue:
    rri: str
    symbol: str
    amount: decimal.Decimal
    price: decimal.Decimal
    value: decimal.Decimal

    def __init__(self, rri, symbol, amount, price: decimal.Decimal):
        self.rri = rri
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.value = round(amount * price, 1)

    def __lt__(self, other: "TokenValue"):
        return self.value < other.value

    @staticmethod
    def print(token_values: ["TokenValue"]):
        total_value: decimal.Decimal = decimal.Decimal("0.00")
        print(f"Token Values:")
        for token_value in token_values:
            total_value += token_value.value
            print(f"{pad(token_value.symbol, 10)} = {pad(disp(token_value.value), 10)} "
                  f"({pad(disp(precision(token_value.amount, 6)), 8)} @{disp(token_value.price)})")
        print(f"Total TOKEN value: ~{disp(total_value)} XRD \n")


async def main():
    """
        Entry point
    """
    client = GatewayClient("https://gateway.radix.live/", debug=False)
    getcontext().prec = 38

    total_balances: dict[str, decimal.Decimal] = dict()
    all_balances: dict[str, dict[str, decimal.Decimal]] = dict()

    for wallet in all_wallets:
        # wallet = all_wallets[0]
        balances: dict[str, str] = await client.get_balances(wallet)
        for resource in balances:
            bal = balances[resource]
            if bal != "0":
                decimal_bal = decimal.Decimal(bal)
                total_balances[resource] = (total_balances[resource] + decimal_bal) \
                    if resource in total_balances \
                    else decimal_bal
                if wallet not in all_balances:
                    all_balances[wallet] = dict()
                all_balances[wallet][resource] = decimal_bal

    print(f"Total Balances: {total_balances}\n")
    print(f"All Balances: {all_balances}\n")

    astro = AstroClient()
    prices, symbols = await astro.get_prices()
    # print(f"Prices: {prices}\n")
    # print(f"Symbols: {symbols}\n")

    token_values: [(str, decimal.Decimal)] = []
    for resource in total_balances:
        if resource in prices:
            token_values.append(
                TokenValue(resource, symbols[resource], total_balances[resource], precision(prices[resource], 5))
            )

    token_values.sort(reverse=True)
    TokenValue.print(token_values)



asyncio.run(main())

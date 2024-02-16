import decimal
from dataclasses import dataclass


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
        if self.value == other.value:
            return self.rri > other.rri
        return self.value < other.value


@dataclass
class AccountBalance:
    account: str
    balance: decimal.Decimal

    def __lt__(self, other: "AccountBalance"):
        if self.balance == other.balance:
            return self.account > other.account
        return self.balance < other.balance


@dataclass
class TokenAccountBalance:
    rri: str
    symbol: str
    amount: decimal.Decimal
    value: decimal.Decimal
    account_balances: list[AccountBalance]

    def __lt__(self, other: "TokenAccountBalance"):
        if self.value == other.value:
            return self.amount < other.amount
        return self.value < other.value

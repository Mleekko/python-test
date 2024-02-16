import dataclasses
import decimal
import json
import sys
from decimal import *

from common import *


def read_wallets(file: str) -> dict[str, str]:
    wallets: dict[str, str] = dict()
    try:
        with open(file, 'r') as f:
            for full_line in f.readlines():
                line = full_line.strip()
                if len(line) > 0 and line.startswith('account_'):
                    parts = line.split(None, 1)
                    wallets[parts[0]] = parts[1].strip() if len(parts) > 1 else line
    except FileNotFoundError:
        print(f"Please create file \"{file}\" with your wallets, one wallet per line", file=sys.stderr)
        exit(404)
    return wallets


def pad(s: str, i: int) -> str:
    if len(s) >= i:
        return s

    return s + " " * (i - len(s))


def disp(num: decimal.Decimal) -> str:
    return format(num, ',')


def precision(num: decimal.Decimal, n=1) -> decimal.Decimal:
    if num.is_zero():
        return num

    order = num.log10().__floor__()
    prec = n - order - 1
    power = decimal.Decimal(10.0 ** prec)
    res = decimal.Decimal((num * power).__round__() / power)
    return res if prec > 0 else res.__round__()


def to_json(obj):
    return json.dumps(obj, indent=2, cls=JSONEncoder)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        elif dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)

        return super().default(o)

import dataclasses
import decimal
import json
import sys


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


def pad(s: str, i: int, right=True) -> str:
    length = len(s)

    if length >= i:
        return s

    if right:
        return s + " " * (i - length)
    else:
        return (" " * (i - length)) + s


SUFFIXES = ['', 'k', 'M', 'B', 'T', 'Q', 'S']


def disp(num: decimal.Decimal) -> str:
    if num.is_zero():
        return '0'

    val = format(num, ',')
    order = 0
    while val.endswith(',000'):
        val = val[0:val.rfind(',000')]
        order += 1
    if val.endswith('00'):
        idx = val.rfind(',')
        if idx > 0 and idx == val.find(','):
            val = val[0:idx] + '.' + val[idx + 1:idx + 2]
            order += 1

    return val + SUFFIXES[order]


def precision(num: decimal.Decimal, n=1) -> decimal.Decimal:
    if num.is_zero():
        return num

    order = num.log10().__floor__()
    prec = n - order - 1
    power = decimal.Decimal("10") ** prec
    res = decimal.Decimal(decimal.Decimal((num * power).__round__()) / power)
    return res if prec > 0 else decimal.Decimal(res.__round__())


def decimals(num: decimal.Decimal, n=2) -> decimal.Decimal:
    return num.quantize(decimal.Decimal('0.' + ('0' * n)))


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

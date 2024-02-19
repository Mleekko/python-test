import json
from dataclasses import dataclass


@dataclass
class ResourceInfo:
    address: str
    symbol: str
    total_supply: str
    pool: str = None
    validator: str = None

    def __init__(self):
        pass

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(self.__dict__, indent=2)


@dataclass
class TokenBalance:
    resource: str
    amount: str

    def __init__(self, resource: str, amount: str):
        self.resource = resource
        self.amount = amount

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.resource + ":" + self.amount


@dataclass
class PoolInfo:
    address: str
    pool_unit_resource: str
    balances: [TokenBalance]

    def __init__(self):
        pass

    def __json__(self):
        fields = self.__dict__.copy()
        fields['balances'] = list(map(lambda x: str(x), self.balances))
        return fields

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(self.__json__(), indent=2)


@dataclass
class ValidatorInfo:
    address: str
    stake_unit_resource: str
    stake_balance: str
    name: str

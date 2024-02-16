import decimal
from decimal import *

from client.astro_client import AstroClient
from client.gateway_client import GatewayClient
from common import *
from model.balance_model import TokenValue, TokenAccountBalance, AccountBalance
from model.gateway_model import ResourceInfo, PoolInfo, TokenBalance
from utils import pad, disp, precision, read_wallets, to_json

NETWORK_ID: int = OlympiaNetwork.MAINNET.value

all_wallets: dict[str, str] = read_wallets('all-wallets.txt')


async def load_balances(client: GatewayClient) -> (dict[str, decimal.Decimal], dict[str, dict[str, decimal.Decimal]]):
    total_balances: dict[str, decimal.Decimal] = dict()
    all_balances: dict[str, dict[str, decimal.Decimal]] = dict()
    for wallet in all_wallets:
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
    return total_balances, all_balances


def calc_pools(all_pools: dict[str, PoolInfo], resources: dict[str, ResourceInfo],
               total_balances: dict[str, decimal.Decimal]) -> (set[str], dict[str, decimal.Decimal]):
    resources_with_pools: set[str] = set()
    pooled_balances: dict[str, decimal.Decimal] = dict()
    for pool_addr in all_pools:
        pool: PoolInfo = all_pools[pool_addr]
        pool_unit_resource = pool.pool_unit_resource
        if pool_unit_resource in resources and resources[pool_unit_resource].pool == pool_addr:
            pool_units: decimal.Decimal = total_balances[pool_unit_resource]
            for token_balance in pool.balances:  # type: TokenBalance
                if token_balance.amount != "0":
                    resources_with_pools.add(pool_unit_resource)
                    bal = (pool_units * decimal.Decimal(token_balance.amount) /
                           decimal.Decimal(resources[pool_unit_resource].total_supply))
                    pooled_balances[token_balance.resource] = (pooled_balances[token_balance.resource] + bal) \
                        if token_balance.resource in pooled_balances \
                        else bal
                    total_balances[token_balance.resource] = (total_balances[token_balance.resource] + bal) \
                        if token_balance.resource in total_balances \
                        else bal
    return resources_with_pools, pooled_balances


def print_pooled_balances(pooled_balances: dict[str, decimal.Decimal], resources: dict[str, ResourceInfo],
                          prices: dict[str, decimal.Decimal]):
    balances = []
    for resource in pooled_balances:
        balances.append({
            'resource': resource,
            'symbol': resources[resource].symbol if resource in resources else '???',
            'xrd_val': pooled_balances[resource] * prices[resource] if resource in prices else decimal.Decimal(0.0),
            'balance': precision(pooled_balances[resource], 6)
        })

    balances.sort(key=lambda b: b['xrd_val'], reverse=True)
    print(f"Pooled Balances: {{")
    for balance in balances:
        print(f"  \"{balance['resource']}\": {pad(disp(balance['balance']), 14)} > {pad(balance['symbol'], 10)}"
              f" ({disp(precision(balance['xrd_val'], 6))} XRD)")
    print(f"}}\n")


def print_token_values(token_values: list[TokenValue]):
    total_value: decimal.Decimal = decimal.Decimal("0.00")
    print(f"Token Values, XRD:")
    for token_value in token_values:
        total_value += token_value.value
        print(f"{pad(token_value.symbol, 10)} = {pad(disp(token_value.value), 10)} "
              f"({pad(disp(precision(token_value.amount, 6)), 8)} @{disp(token_value.price)})")
    print(f"Total TOKEN value: ~{disp(total_value)} XRD \n")


def print_account_balances(account_balances: list[TokenAccountBalance]):
    print(f"Account Balances:")
    for account_balance in account_balances:
        lines = '\n'.join(pad('', 10) + pad(all_wallets[b.account], 66) + '=' + disp(precision(b.balance, 10)) for b in account_balance.account_balances)
        print(f"({account_balance.rri}):       {pad(disp(precision(account_balance.amount, 10)), 13)} {account_balance.symbol}\n{lines}\n")


async def main():
    """
        Entry point
    """
    client = GatewayClient("https://gateway.radix.live/", debug=False)
    getcontext().prec = 38

    total_balances, all_balances = await load_balances(client)  # type: (dict[str, decimal.Decimal], dict[str, dict[str, decimal.Decimal]])
    # print(f"All Balances: {to_json(all_balances)}\n")

    resources: dict[str, ResourceInfo] = await client.get_resources(list(total_balances.keys()))

    pools: list[str] = list()
    for resource in resources.values():
        if total_balances[resource.address] > 0 and resource.pool is not None:
            pools.append(resource.pool)

    all_pools: dict[str, PoolInfo] = await client.get_pools(pools)

    resources_with_pools, pooled_balances = calc_pools(all_pools, resources, total_balances)  # type: (set[str], dict[str, decimal.Decimal])

    astro = AstroClient()
    prices, symbols = await astro.get_prices()  # type: (dict[str, decimal.Decimal], dict[str, str])

    total_values: dict[str, TokenValue] = dict()
    for resource in total_balances:
        if resource in prices and resource not in resources_with_pools:
            total_values[resource] = TokenValue(resource, resources[resource].symbol, total_balances[resource], precision(prices[resource], 5))

    token_values: list[TokenValue] = list(total_values.values())
    token_values.sort(reverse=True)

    token_account_balances: dict[str, TokenAccountBalance] = dict()
    for account in all_balances:
        balances = all_balances[account]
        for resource in balances:
            if resource not in token_account_balances:
                symbol = resources[resource].symbol if resource in resources else '???'
                resource__value = total_values[resource].value if resource in total_values else decimal.Decimal(0)
                token_account_balances[resource] = TokenAccountBalance(resource, symbol, decimal.Decimal(0), resource__value, [])
            token_account_balance = token_account_balances[resource]
            token_account_balance.amount += balances[resource]
            token_account_balance.account_balances.append(AccountBalance(account, balances[resource]))
    token_account_balances_list = list(token_account_balances.values())
    for bal in token_account_balances_list:
        bal.account_balances.sort(reverse=True)
    token_account_balances_list.sort(reverse=True)

    print_account_balances(token_account_balances_list)
    print_pooled_balances(pooled_balances, resources, prices)
    print_token_values(token_values)

asyncio.run(main())

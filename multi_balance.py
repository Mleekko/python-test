import decimal
from decimal import *

from radix_engine_toolkit import OlympiaNetwork

from client.astro_client import AstroClient
from client.gateway_client import GatewayClient
from common import *
from model.balance_model import TokenValue, TokenAccountBalance, AccountBalance
from model.gateway_model import ResourceInfo, PoolInfo, TokenBalance, ValidatorInfo
from utils import pad, disp, precision, read_wallets, to_json, decimals

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


def calc_pools(our_pools: dict[str, PoolInfo], resources: dict[str, ResourceInfo],
               total_balances: dict[str, decimal.Decimal], excluded_resources: set[str]) -> (set[str], dict[str, decimal.Decimal]):
    pooled_balances: dict[str, decimal.Decimal] = dict()
    for pool_addr in our_pools:
        pool: PoolInfo = our_pools[pool_addr]
        pool_unit_resource = pool.pool_unit_resource
        if pool_unit_resource in resources and resources[pool_unit_resource].pool == pool_addr:
            pool_units: decimal.Decimal = total_balances[pool_unit_resource]
            for token_balance in pool.balances:  # type: TokenBalance
                if token_balance.amount != "0":
                    excluded_resources.add(pool_unit_resource)
                    bal = (pool_units * decimal.Decimal(token_balance.amount) /
                           decimal.Decimal(resources[pool_unit_resource].total_supply))
                    pooled_balances[token_balance.resource] = (pooled_balances[token_balance.resource] + bal) \
                        if token_balance.resource in pooled_balances \
                        else bal
                    total_balances[token_balance.resource] = (total_balances[token_balance.resource] + bal) \
                        if token_balance.resource in total_balances \
                        else bal
    return pooled_balances


def calc_staked_values(our_validators: dict[str, ValidatorInfo], resources: dict[str, ResourceInfo],
                       total_balances: dict[str, decimal.Decimal], excluded_resources: set[str]) -> list[AccountBalance]:
    staked_values: list[AccountBalance] = list()
    for validator_addr in our_validators:
        validator: ValidatorInfo = our_validators[validator_addr]
        stake_unit_resource = validator.stake_unit_resource
        if stake_unit_resource in resources and resources[stake_unit_resource].validator == validator_addr:
            pool_units: decimal.Decimal = total_balances[stake_unit_resource]
            if validator.stake_balance != "0":
                excluded_resources.add(stake_unit_resource)
                bal = (pool_units * decimal.Decimal(validator.stake_balance) /
                       decimal.Decimal(resources[stake_unit_resource].total_supply))
                staked_values.append(AccountBalance(validator_addr, bal))

    staked_values.sort(reverse=True)
    return staked_values


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


def print_validator_stakes(staked_values: list[AccountBalance], our_validators: dict[str, ValidatorInfo]):
    print(f"Validator stakes, XRD:")
    for value in staked_values:
        validator = our_validators[value.account]
        print(f"{pad(validator.name, 20)} -> {pad(disp(precision(value.balance, 6)), 18)} [{value.account}]")
    print("")


def print_token_values(token_values: list[TokenValue], pooled_balances: dict[str, decimal.Decimal], staked_values: list[AccountBalance]):
    total_value: decimal.Decimal = decimal.Decimal("0.00")
    print(f"Token Values, XRD:")
    for token_value in token_values:
        total_value += token_value.value
        pooled_amount = pooled_balances[token_value.rri] if token_value.rri in pooled_balances else decimal.Decimal(0)
        main_amount = token_value.amount - pooled_amount
        pooled_str = f" {disp(precision(main_amount, 6))} + {disp(precision(pooled_amount, 6))} " if pooled_amount > 0 else ''
        print(f"{pad(token_value.symbol, 10)} = {pad(disp(token_value.value), 11)} "
              f"{pad('| '+pad(disp(precision(token_value.amount, 6)), 11) + ' @' + disp(token_value.price), 28)}"
              f"{pooled_str}")

    total_staked = decimals(decimal.Decimal(sum(val.balance for val in staked_values)), 2)
    values = [
        disp(total_value),
        disp(total_staked),
        disp(total_value + total_staked)
    ]
    max_width = max(len(s) for s in values)
    print(f"Total TOKEN value: ~{pad(values[0], max_width, False)} XRD")
    print(f"Total Staked:       {pad(values[1], max_width, False)} XRD")
    print(f"Total + Staked:    ~{pad(values[2], max_width, False)} XRD\n")


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

    print(f"Loading balances...")
    total_balances, all_balances = await load_balances(client)  # type: (dict[str, decimal.Decimal], dict[str, dict[str, decimal.Decimal]])

    print(f"Loading resources...")
    resources: dict[str, ResourceInfo] = await client.get_resources(list(total_balances.keys()))

    pools: list[str] = list()
    validators: set[str] = set()
    for resource in resources.values():
        if total_balances[resource.address] > 0:
            if resource.pool is not None:
                pools.append(resource.pool)
            elif resource.validator is not None:
                validators.add(resource.validator)

    print(f"Loading pools...")
    our_pools: dict[str, PoolInfo] = await client.get_pools(pools)

    excluded_resources: set[str] = set()
    pooled_balances = calc_pools(our_pools, resources, total_balances, excluded_resources)  # type: dict[str, decimal.Decimal]

    print(f"Loading Pooled resources...")
    res_to_load = list(pooled_balances.keys() - resources.keys())
    if len(res_to_load) > 0:
        resources2: dict[str, ResourceInfo] = await client.get_resources(res_to_load)
        resources.update(resources2)

    print(f"Loading prices...")
    astro = AstroClient()
    prices, symbols = await astro.get_prices()  # type: (dict[str, decimal.Decimal], dict[str, str])

    our_validators: dict[str, ValidatorInfo] = dict()
    if len(validators) > 0:
        print(f"Loading Validators...")
        our_validators = await client.load_validators(validators)
    staked_values: list[AccountBalance] = calc_staked_values(our_validators, resources, total_balances, excluded_resources)

    total_values: dict[str, TokenValue] = dict()
    for resource in total_balances:
        if resource in prices and resource not in excluded_resources:
            total_values[resource] = TokenValue(resource, resources[resource].symbol, total_balances[resource], precision(prices[resource], 5))

    token_values: list[TokenValue] = list(total_values.values())
    token_values.sort()

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
    print_validator_stakes(staked_values, our_validators)
    print_token_values(token_values, pooled_balances, staked_values)

asyncio.run(main())

import json
from typing import Callable, Any

import httpx

from model.gateway_model import ResourceInfo, PoolInfo, TokenBalance, ValidatorInfo


class GatewayClient:
    gateway_url: str
    session: httpx.AsyncClient
    _debug: bool

    def __init__(self, gateway_url: str, debug: bool = True):
        self.gateway_url = gateway_url if gateway_url.endswith('/') else gateway_url + '/'
        self.session = httpx.AsyncClient(follow_redirects=True, http2=True)
        self._debug = debug

    async def get_current_epoch(self) -> int:
        r = await self.session.get(self.gateway_url, headers={
            'Accept': 'application/json'
        })
        if self._debug:
            print(f"Response: {r.text}\n")
        data = r.json()
        return data['gateway']['ledger_state']['epoch']

    async def submit_transaction(self, tx_hex: str) -> bool:
        data = await self.__do_post('transaction/submit', {
            "notarized_transaction_hex": tx_hex
        })

        return data['duplicate']

    async def get_balances(self, account: str, include_non_fungibles=False) -> dict[str, str]:
        balances = dict()

        cursor = None
        state_version = 0

        while state_version == 0 or cursor is not None:
            request_body = {
                "address": account
            }
            if cursor is not None:
                request_body = {
                    "address": account,
                    "cursor": cursor,
                    "at_ledger_state": {"state_version": state_version},
                }
            data = await self.__do_post('state/entity/page/fungibles', request_body)

            cursor = data['next_cursor'] if 'next_cursor' in data else None
            state_version = data['ledger_state']['state_version']

            for item in data['items']:
                balances[item['resource_address']] = item['amount']

        return balances

    async def get_resources(self, addresses: [str]) -> dict[str, ResourceInfo]:
        all_resources: dict[str, ResourceInfo] = dict()

        def convert(data: dict):
            for item in data['items']:
                # print(f"item: {item}\n")
                info: ResourceInfo = ResourceInfo()
                info.address = item['address']
                info.symbol = '?'
                info.total_supply = item['details']['total_supply']
                for meta_item in item['metadata']['items']:
                    meta_item_key = meta_item['key']
                    if meta_item_key == 'symbol':
                        info.symbol = meta_item['value']['programmatic_json']['fields'][0]['value'].upper()
                    elif meta_item_key == 'name' and info.symbol == '?':
                        info.symbol = meta_item['value']['programmatic_json']['fields'][0]['value']
                    elif meta_item_key == 'pool':
                        info.pool = meta_item['value']['programmatic_json']['fields'][0]['value']
                    elif meta_item_key == 'validator':
                        info.validator = meta_item['value']['programmatic_json']['fields'][0]['value']

                all_resources[info.address] = info

        await self.__load_details(addresses, convert)

        return all_resources

    async def get_pools(self, addresses: [str]) -> dict[str, PoolInfo]:
        all_pools: dict[str, PoolInfo] = dict()

        def convert(data: dict):
            for item in data['items']:
                info: PoolInfo = PoolInfo()
                info.address = item['address']
                info.pool_unit_resource = item['details']['state']['pool_unit_resource_address']
                info.balances = list()
                for fungible_item in item['fungible_resources']['items']:
                    vaults_items = fungible_item['vaults']['items']
                    if len(vaults_items) != 1:
                        raise RuntimeError('I cannot handle ' + str(len(vaults_items))
                                           + ' vaults in pool: ' + info.address)
                    info.balances.append(TokenBalance(
                        fungible_item['resource_address'], vaults_items[0]['amount']
                    ))

                all_pools[info.address] = info

        await self.__load_details(addresses, convert)

        return all_pools

    async def load_validators(self, validators: set[str]) -> dict[str, ValidatorInfo]:
        data = await self.__do_post('state/validators/list', {})

        all_validators: dict[str, ValidatorInfo] = dict()

        for item in data['validators']['items']:
            address: str = item['address']
            if address in validators:
                stake_unit_resource = item['state']['stake_unit_resource_address']
                name = '???'
                for meta_item in item['metadata']['items']:
                    if meta_item['key'] == 'name':
                        name = meta_item['value']['programmatic_json']['fields'][0]['value']
                all_validators[address] = ValidatorInfo(address, stake_unit_resource, item['stake_vault']['balance'], name)
        return all_validators

    async def get_entity(self, address: str) -> dict[str, Any]:
        entity = dict()

        def convert(data: dict):
            entity.update(data['items'][0])

        await self.__load_details([address], convert)

        return entity

    async def __do_post(self, url, request_body):
        r = await self.session.post(self.gateway_url + url, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, content=json.dumps(request_body))

        if self._debug:
            print(f"Response: {r.text}\n")
        return r.json()

    async def __load_details(self, addresses: [str], data_consumer: Callable[[dict], None]):
        addresses_batches: list[list[str]] = [addresses[i:(i + 20)] for i in range(0, len(addresses), 20)]
        for address_batch in addresses_batches:
            data = await self.__do_post('state/entity/details', {
                "addresses": address_batch,
                "aggregation_level": "Vault"
            })

            data_consumer(data)

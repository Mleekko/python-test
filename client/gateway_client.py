import json

import httpx


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
        r = await self.session.post(self.gateway_url + 'transaction/submit', headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }, content=json.dumps({
            "notarized_transaction_hex": tx_hex
        }))

        if self._debug:
            print(f"Response: {r.text}\n")
        data = r.json()
        return data['duplicate']

    async def get_balances(self, account: str) -> dict[str, str]:
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
            r = await self.session.post(self.gateway_url + 'state/entity/page/fungibles', headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }, content=json.dumps(request_body))

            if self._debug:
                print(f"Response: {r.text}\n")

            data = r.json()

            cursor = data['next_cursor'] if 'next_cursor' in data else None
            state_version = data['ledger_state']['state_version']

            for item in data['items']:
                balances[item['resource_address']] = item['amount']

        return balances

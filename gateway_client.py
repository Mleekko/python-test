import json

import httpx


class GatewayClient:
    gateway_url: str
    session: httpx.AsyncClient

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url if gateway_url.endswith('/') else gateway_url + '/'
        self.session = httpx.AsyncClient(follow_redirects=True, http2=True)

    async def get_current_epoch(self) -> int:
        r = await self.session.get(self.gateway_url, headers={
            'Accept': 'application/json'
        })
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

        print(f"Response: {r.text}\n")
        data = r.json()
        return data['duplicate']

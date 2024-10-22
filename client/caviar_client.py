import decimal

import httpx


class CaviarClient:
    session: httpx.AsyncClient

    def __init__(self):
        self.session = httpx.AsyncClient(follow_redirects=True, http2=True)

    async def get_prices(self) -> dict[str, decimal.Decimal]:
        r = await self.session.get("https://api-core.caviarnine.com/v1.0/public/tokens", headers={
            'Accept': 'application/json'
        })
        # print(f"Response: {r.text}\n")
        data = r.json()

        prices: dict[str, decimal.Decimal] = dict()
        for resource in data['data']:
            price_to_xrd = data['data'][resource]['price_to_xrd']
            mid_price = price_to_xrd['mid']
            bid_price = price_to_xrd['bid']
            if mid_price is not None and bid_price is not None and decimal.Decimal(bid_price) > 0:
                prices[resource] = decimal.Decimal(mid_price)

        return prices

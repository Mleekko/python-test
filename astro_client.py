import decimal
import json

import httpx


class AstroClient:
    session: httpx.AsyncClient

    def __init__(self):
        self.session = httpx.AsyncClient(follow_redirects=True, http2=True)

    async def get_prices(self) -> (dict[str, decimal.Decimal], dict[str, str]):
        r = await self.session.get("https://astrolescent.com/?index")

        start_idx: int = r.text.find("window.__remixContext")
        start_idx: int = r.text.find("{", start_idx)
        end_idx: int = r.text.find("</script>", start_idx)
        end_idx: int = r.text.rfind("}", start_idx, end_idx)

        json_data = r.text[start_idx:end_idx + 1]
        # print(f"json_data: {json_data}\n")
        data = json.loads(json_data)
        tokens_data = data['state']['loaderData']['routes/_index']['tokens']

        prices: dict[str, decimal.Decimal] = dict()
        symbols: dict[str, str] = dict()
        for token in tokens_data:
            symbols[token['address']] = token['symbol'].upper()
            token_price_xrd = token['tokenPriceXRD']
            if token_price_xrd is not None:
                prices[token['address']] = decimal.Decimal(token_price_xrd)

        return prices, symbols

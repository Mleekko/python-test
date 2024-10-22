import decimal
import json
from codecs import encode, decode

import httpx


class AstroClient:
    session: httpx.AsyncClient

    def __init__(self):
        self.session = httpx.AsyncClient(follow_redirects=True, http2=True)

    async def get_prices(self) -> dict[str, decimal.Decimal]:
        r = await self.session.get("https://astrolescent.com/?index")

        start_idx: int = r.text.find("window.__remixContext.streamController.enqueue(\"")
        start_idx: int = r.text.find("[", start_idx)
        end_idx: int = r.text.find("</script>", start_idx)
        end_idx: int = r.text.rfind("\");", start_idx, end_idx)

        json_string = r.text[start_idx:end_idx + 1]
        print(f"json_string: {json_string}\n")

        data = json.loads(decode(json_string, 'unicode_escape'))
        tokens_data = data['state']['loaderData']['routes/_app._index']['tokens']

        prices: dict[str, decimal.Decimal] = dict()
        for token in tokens_data:
            token_price_xrd = token['tokenPriceXRD']
            if token_price_xrd is not None:
                prices[token['address']] = decimal.Decimal(token_price_xrd)

        return prices

from datetime import datetime, timezone
from py_clob_client.client import ClobClient
import requests
import json
ETH_TAG_ID = 39
TIMEFRAME_TAG_ID = 102467

client = ClobClient("https://clob.polymarket.com", chain_id=137)
def parse_datetime(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_market_window(market):
    market_entries = market.get("markets") or [{}]
    start_time = (
        market.get("startTime")
        or market_entries[0].get("eventStartTime")
        or market.get("startDate")
    )
    end_time = market.get("endDate")

    if not start_time or not end_time:
        return None, None

    return parse_datetime(start_time), parse_datetime(end_time)


def get_current_market(markets):
    now = datetime.now(timezone.utc)

    for market in markets:
        tag_ids = {int(tag["id"]) for tag in market.get("tags", [])}
        if not {ETH_TAG_ID, TIMEFRAME_TAG_ID}.issubset(tag_ids):
            continue

        start_time, end_time = get_market_window(market)
        if not start_time or not end_time:
            continue

        if start_time <= now < end_time:
            return market

    return None


url = (
    "https://gamma-api.polymarket.com/events"
    f"?tag_id={TIMEFRAME_TAG_ID}&limit=50&active=true&closed=false"
)

response = requests.get(url)
response.raise_for_status()
market = get_current_market(response.json())
if market:
    m = market["markets"][0]
    
    print(f"Outcomes : {m['outcomes']}\n Ids : {m['clobTokenIds']}")
else:
    exit("No active market found with the specified tags.")

m["outcomes"] = json.loads(m["outcomes"])
m["clobTokenIds"] = json.loads(m["clobTokenIds"])


print(m['outcomes'][0])
if m['outcomes'][0] == "Up":
    book = client.get_order_book(m['clobTokenIds'][0])
    bestask = book.asks[-1]
    bestbid = book.bids[-1]
    print(f"UP : Best Ask : {bestask.price} | Best Bid : {bestbid.price}")
if m['outcomes'][1] == "Down":
    book = client.get_order_book(m['clobTokenIds'][1])
    bestask = book.asks[-1]
    bestbid = book.bids[-1]
    print(f"DOWN : Best Ask : {bestask.price} | Best Bid : {bestbid.price}")

    




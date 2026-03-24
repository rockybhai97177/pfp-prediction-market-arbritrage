import requests
import time
url = "https://api.limitless.exchange/markets/active"

response = requests.get(url)
market = None
r = response.json()
for m in r["data"]:
    if "Minutes 15" in m["tags"] and "eth" in m["slug"]  :
        market = m
while True:
    if market:
        print(f"Market: {market['slug']} RELOADING")
        url = f"https://api.limitless.exchange/markets/{market['slug']}/orderbook"
        response = requests.get(url)
        for i in response.json()["asks"]:
            print(f"ask price: {i['price']} size: {i['size']}")
    time.sleep(3)
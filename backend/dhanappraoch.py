from dhanhq import DhanContext, MarketFeed

client_id=""
access_token=""

dhan_context = DhanContext(client_id, access_token)

instruments = [
    (MarketFeed.NSE, "2885", MarketFeed.Ticker)   # Reliance
]

data = MarketFeed(dhan_context, instruments, "v2")
import time

data.run_forever()
print("Connected")

time.sleep(2)

try:
    while True:
        response = data.get_data()
        print(response)
except Exception as e:
    print(e)

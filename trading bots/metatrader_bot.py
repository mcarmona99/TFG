# Ejemplo bot trading
import pandas as pd
from binance.client import Client

API_KEY = 'k6pgv5tnpbr60CuKHmP9mBNVr3mCsKPXVqVy6AyqhEc8XOUesTxO9x2Ex1rWCVfN'
API_SECRET = 'r0KcFLBi473zZngFYFvAotXkLkauVbxBFjtQPlKh7zFnje8HeKe8jl6J9f5CIAdh'
SYMBOL = 'ETHUSDT'

if __name__ == '__main__':
    # Crear cliente de binance
    # Client( API_KEY, API_SECRET )
    print('Logging into Binance ...')
    client = Client(api_key=API_KEY, api_secret=API_SECRET)

    # tickers = client.get_orderbook_tickers()
    #
    # print(tickers)

    orderbook = client.get_order_book(symbol=SYMBOL)

    ob = pd.DataFrame(orderbook)

    print(ob)

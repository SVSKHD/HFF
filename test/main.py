from datetime import datetime
from fetch import fetch_price
from utils import connect_mt5
from config import symbols_config
from logic import decide_trade
import asyncio


async def main():
    today = datetime.now()
    connect =  await connect_mt5()
    if connect:
        if 0 <= today.hour <=13:
            print("Trading is allowed")
            for symbol in symbols_config:
                start_price=fetch_price(symbol, "start")
                current_price=fetch_price(symbol, "current")
                decide_trade(symbol, start_price, current_price)
                print(f"Start price for {symbol['symbol']} is {start_price} current is {current_price} difference is {current_price-start_price}")
        else:
            print(f"Monitoring {connect}")


if __name__ == "__main__":
    asyncio.run(main())
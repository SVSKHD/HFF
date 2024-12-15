from datetime import datetime
from fetch import fetch_price
from utils import connect_mt5
from config import symbols_config
from logic import decide_trade
import asyncio
from db import get_symbol_data, clear_all_keys


def execute_trade(symbol):
    """
    Executes trade logic based on thresholds for the given symbol.
    """
    symbol_name = symbol['symbol']
    symbol_data = get_symbol_data(symbol_name)

    if not symbol_data:
        print(f"No data available for {symbol_name}")
        return  # Exit if no symbol data is available

    # Retrieve necessary fields from symbol_data
    thresholds_no = symbol_data.get('thresholds_no')
    threshold_reached = symbol_data.get('threshold_reached', False)
    hedging = symbol_data.get('hedging', False)

    if thresholds_no is None:
        print(f"Missing thresholds_no for {symbol_name}")
        return  # Exit if thresholds_no is missing

    print(f"Processing {symbol_name}: thresholds_no={thresholds_no}, threshold_reached={threshold_reached}, hedging={hedging}")

    # Trade execution logic for positive thresholds
    if thresholds_no > 1.2:
        print(f"Threshold exceeded for {symbol_name} - Placing buy order.")
        # place_order(symbol, symbol_data)
    elif 1 <= thresholds_no <= 1.2:
        print(f"Placing trade for {symbol_name} in positive range (1 to 1.2).")
        # place_order(symbol, symbol_data)

    # Trade execution logic for negative thresholds
    if thresholds_no < -1.2:
        print(f"Threshold exceeded for {symbol_name} - Placing sell order.")
        # place_order(symbol, symbol_data)
    elif -1.2 <= thresholds_no <= -1:
        print(f"Placing trade for {symbol_name} in negative range (-1.2 to -1).")
        # place_order(symbol, symbol_data)

    # Closing trades at extreme thresholds
    if thresholds_no >= 2 or thresholds_no <= -2:
        print(f"Threshold exceeded for {symbol_name} - Closing trades.")
        # close_trade_symbol(symbol)

    # Hedging logic
    if threshold_reached and hedging:  # Ensure hedging is enabled and threshold is reached
        if thresholds_no >= 0.95:
            print(f"Closing trades for {symbol_name} due to hedging and thresholds_no >= 0.95.")
            # close_trade_symbol(symbol)
        elif thresholds_no <= -0.95:
            print(f"Closing trades for {symbol_name} due to hedging and thresholds_no <= -0.95.")
            # close_trade_symbol(symbol)
        elif 0.5 <= thresholds_no < 1:
            print(f"Hedging triggered for {symbol_name} - Closing trades on positive threshold.")
            # place_trade(symbol)
        elif -1 < thresholds_no <= -0.5:
            print(f"Hedging triggered for {symbol_name} - Closing trades on negative threshold.")
            # place_trade(symbol)



async def main():
    today = datetime.now()
    connect =  await connect_mt5()
    if connect:
        if 0 <= today.hour < 23:
            print("Trading is allowed")
            for symbol in symbols_config:
                start_price=fetch_price(symbol, "start")
                current_price=fetch_price(symbol, "current")
                decide_trade(symbol, start_price, current_price)
                print(f"Start price for {symbol['symbol']} is {start_price} current is {current_price} difference is {current_price-start_price/symbol['threshold']}")

        else:
            clear_all_keys()()
            print(f"Monitoring {connect}")


if __name__ == "__main__":
    asyncio.run(main())
from HFF.test.logic import threshold_no
from config import symbols_config
from datetime import datetime
import asyncio
from utils import connect_mt5
from fetch import fetch_price
from db import get_symbol_data
from logic import decide_trade_and_thresholds
from trade_place import place_order, close_trades_by_symbol

def initiate_trade(symbol):
    symbol_name = symbol['symbol']
    lot_size = symbol['lot_size']
    symbol_data = get_symbol_data(symbol_name)
    if symbol_data is not None:
        threshold_no = symbol_data['threshold_no']
        pip_difference = symbol_data['pip_difference']
        direction = symbol_data['direction']
        hedging = symbol_data['hedging']
        positive_hedging = symbol_data['positive_hedging']
        negative_hedging = symbol_data['negative_hedging']

        first_positive_threshold = symbol_data['first_positive_threshold']
        first_negative_threshold = symbol_data['first_negative_threshold']
        second_positive_threshold = symbol_data['second_positive_threshold']
        second_negative_threshold = symbol_data['second_negative_threshold']

        # Example conditions based on assumed logic:
        if first_positive_threshold and 1 < threshold_no < 1.2:
            place_order(symbol, "buy", lot_size, hedging)
        elif first_negative_threshold and -1.2 < threshold_no < -1:
            place_order(symbol, "sell", lot_size, hedging)
        elif second_positive_threshold:
            close_trades_by_symbol(symbol)
        elif second_negative_threshold:
            close_trades_by_symbol(symbol)

        if hedging:
            if positive_hedging:
                place_order(symbol, "buy", lot_size, hedging)
            elif negative_hedging:
                place_order(symbol, "sell", lot_size, hedging)






def monitor_trades(symbol):
    symbol_name = symbol['symbol']
    symbol_data = get_symbol_data(symbol_name)
    lot_size = symbol['lot_size']

    if symbol_data is not None:
        threshold_no = symbol_data['threshold_no']
        pip_difference = symbol_data['pip_difference']
        direction = symbol_data['direction']
        hedging = symbol_data['hedging']
        positive_hedging = symbol_data['positive_hedging']
        negative_hedging = symbol_data['negative_hedging']
        second_positive_threshold = symbol_data['second_positive_threshold']
        second_negative_threshold = symbol_data['second_negative_threshold']

        if second_positive_threshold:
            close_trades_by_symbol(symbol)
        if second_negative_threshold:
            close_trades_by_symbol(symbol)

        if hedging:
            if positive_hedging:
                place_order(symbol, "buy", lot_size, hedging)
            elif negative_hedging:
                place_order(symbol, "sell", lot_size, hedging)







async def main():
    while True:
        try:
            # Connect to MT5
            connect = await connect_mt5()
            if not connect:
                print("Failed to connect to MetaTrader 5. Retrying...")
                await asyncio.sleep(5)
                continue

            # Get current time
            today = datetime.now()

            if 0 <= today.hour < 12:  # Trading hours check
                print("Processing trades during trading hours...")
                for symbol in symbols_config:
                    try:
                        # Fetch start and current prices
                        start_price = fetch_price(symbol, "start")
                        current_price = fetch_price(symbol, "current")

                        # Decide trade and thresholds
                        await decide_trade_and_thresholds(symbol, start_price, current_price)
                        initiate_trade(symbol)
                    except Exception as e:
                        print(f"Error processing symbol {symbol['symbol']}: {e}")
            else:
                print("Outside trading hours. Cleared all keys.")
                for symbol in symbols_config:
                    try:
                        # Fetch start and current prices
                        start_price = fetch_price(symbol, "start")
                        current_price = fetch_price(symbol, "current")

                        # Decide trade and thresholds
                        await decide_trade_and_thresholds(symbol, start_price, current_price)
                        monitor_trades(symbol)
                    except Exception as e:
                        print(f"Error processing symbol {symbol['symbol']}: {e}")

            # Sleep before the next iteration
            await asyncio.sleep(1)

        except Exception as main_exception:
            print(f"Unexpected error in main loop: {main_exception}")
            await asyncio.sleep(1)  # Wait before retrying

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())

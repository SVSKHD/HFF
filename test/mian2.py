from config import symbols_config
from datetime import datetime
import asyncio
from utils import connect_mt5
from fetch import fetch_price
from logic2 import decide_trade_and_thresholds

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
                        decide_trade_and_thresholds(symbol, start_price, current_price)
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
                        decide_trade_and_thresholds(symbol, start_price, current_price)
                    except Exception as e:
                        print(f"Error processing symbol {symbol['symbol']}: {e}")

            # Sleep before the next iteration
            await asyncio.sleep(60)

        except Exception as main_exception:
            print(f"Unexpected error in main loop: {main_exception}")
            await asyncio.sleep(1)  # Wait before retrying

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())

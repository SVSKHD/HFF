from datetime import datetime
from fetch import fetch_price
from utils import connect_mt5
from config import symbols_config
from logic import decide_trade
import asyncio
from db import get_symbol_data, clear_all_keys
from trade_place import place_order, close_trades_by_symbol
import logging


async def execute_trade(symbol):
    """
    Executes trade logic asynchronously based on thresholds for the given symbol.
    """
    symbol_name = symbol['symbol']
    symbol_data = get_symbol_data(symbol_name)

    if not symbol_data:
        logging.warning(f"No data available for {symbol_name}")
        return  # Exit if no symbol data is available

    # Retrieve necessary fields from symbol_data
    thresholds_no = symbol_data.get('thresholds_no')
    threshold_reached = symbol_data.get('threshold_reached', False)
    hedging = symbol_data.get('hedging', False)

    if thresholds_no is None:
        logging.error(f"Missing thresholds_no for {symbol_name}")
        return  # Exit if thresholds_no is missing

    logging.info(f"Processing {symbol_name}: thresholds_no={thresholds_no}, threshold_reached={threshold_reached}, hedging={hedging}")

    # Prevent new trades if thresholds_no has already crossed ±2
    if thresholds_no >= 2 or thresholds_no <= -2:
        logging.info(f"Threshold for {symbol_name} has already crossed ±2. No new trades will be placed.")
        await close_trades_by_symbol(symbol)  # Close trades if needed, but do not place new ones
        return

    # Trade execution logic
    try:
        if thresholds_no > 1.2:
            logging.info(f"Threshold exceeded for {symbol_name} - Placing buy order.")
            await place_order(symbol, 'sell', symbol['lot_size'], False)

        elif 1 <= thresholds_no <= 1.2:
            logging.info(f"Placing trade for {symbol_name} in positive range (1 to 1.2).")
            await place_order(symbol, 'sell', symbol['lot_size'], False)

        if thresholds_no < -1.2:
            logging.info(f"Threshold exceeded for {symbol_name} - Placing sell order.")
            await place_order(symbol, 'buy', symbol['lot_size'], False)
        elif -1.2 <= thresholds_no <= -1:
            logging.info(f"Placing trade for {symbol_name} in negative range (-1.2 to -1).")
            await place_order(symbol, 'buy', symbol['lot_size'], False)

        # Hedging logic
        if threshold_reached and hedging:
            if thresholds_no >= 0.95:
                logging.info(f"Closing trades for {symbol_name} due to hedging and thresholds_no >= 0.95.")
                await close_trades_by_symbol(symbol)
            elif thresholds_no <= -0.95:
                logging.info(f"Closing trades for {symbol_name} due to hedging and thresholds_no <= -0.95.")
                await close_trades_by_symbol(symbol)
    except Exception as e:
        logging.error(f"Error executing trade for {symbol_name}: {e}")


async def monitor_trading():
    """
    Continuously monitors the market and executes trades every minute.
    """
    while True:
        today = datetime.now()
        connect = await connect_mt5()

        if connect:
            logging.info("Connected to MT5. Starting trading loop.")
            if 0 <= today.hour < 23:
                for symbol in symbols_config:
                    try:
                        start_price = fetch_price(symbol, "start")
                        current_price = fetch_price(symbol, "current")

                        if start_price is None or current_price is None:
                            logging.warning(f"Price data unavailable for {symbol['symbol']}. Skipping.")
                            continue

                        logging.info(
                            f"Start price for {symbol['symbol']} is {start_price}, current is {current_price}, "
                            f"difference is {current_price - start_price / symbol['threshold']}."
                        )

                        decide_trade(symbol, start_price, current_price)
                        await execute_trade(symbol)  # Use await for async execution
                        logging.info(f"Finished processing {symbol['symbol']}.")
                    except Exception as e:
                        logging.error(f"Error processing symbol {symbol['symbol']}: {e}")
            else:
                clear_all_keys()
                logging.info("Outside trading hours. Cleared all keys.")

        else:
            logging.error("Failed to connect to MT5.")

        await asyncio.sleep(1)  # Wait for 1 minute before next iteration


if __name__ == "__main__":
    asyncio.run(monitor_trading())
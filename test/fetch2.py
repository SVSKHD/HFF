from datetime import timezone, datetime, timedelta
import MetaTrader5 as mt5


def fetch_price(symbol_data, fetch_type):
    # Extract the symbol name
    server_timezone = timezone.utc  # Set to UTC or your broker's timezone
    symbol_name = symbol_data.get('symbol')
    if not symbol_name:
        raise ValueError("Symbol name is missing in symbol_data.")

    # Get the current date and time
    current_date = datetime.now()
    day_of_week = current_date.strftime("%A")
    target_timestamp = None

    # Initialize MT5
    if not mt5.initialize():
        print("MetaTrader5 initialization failed.")
        return None

    if fetch_type == 'current':
        # Fetch current price for the symbol
        tick = mt5.symbol_info_tick(symbol_name)
        if tick:
            current_price = tick.bid
            print(f"Fetching current price for {symbol_name}: {current_price}")
            return current_price
        else:
            print(f"Failed to fetch current price for {symbol_name}.")
            return None

    elif fetch_type == 'start':
        # Determine target timestamp
        if day_of_week in ['Sunday', 'Saturday', 'Monday']:
            # Calculate the most recent Friday
            days_since_friday = (current_date.weekday() - 4) % 7
            last_friday = current_date - timedelta(days=days_since_friday)

            # Add specific time to last Friday (23:58:59) in the server timezone
            target_time = datetime(
                last_friday.year, last_friday.month, last_friday.day,
                23, 58, 59, tzinfo=server_timezone
            )
        else:
            # Use the present day's date at 12:00 AM
            target_time = datetime(
                current_date.year, current_date.month, current_date.day,
                0, 0, 0, tzinfo=server_timezone
            )

        formatted_date = target_time.strftime("%Y-%m-%d %H:%M:%S")
        target_timestamp = int(target_time.timestamp())

        # Fetch price data for the target timestamp
        ticks = mt5.copy_ticks_from(symbol_name, target_timestamp, 1, mt5.COPY_TICKS_INFO)
        if ticks is not None and len(ticks) > 0:
            start_price = ticks['bid'][0]  # Accessing the 'bid' field correctly
            return start_price
        else:
            print(f"Failed to fetch start price for {symbol_name}. Ensure sufficient tick data is available.")
            return None

    elif fetch_type == '5min':
        # Define the timeframe (5 minutes) and number of bars
        timeframe = mt5.TIMEFRAME_M5
        num_bars = 1  # Fetch the most recent 5-minute candle

        # Fetch 5-minute timeframe data
        rates = mt5.copy_rates_from(symbol_name, timeframe, datetime.now(), num_bars)
        if rates is not None and len(rates) > 0:
            # Extract the last 5-minute candle close price
            five_min_price = rates[-1]['close']
            print(f"Fetching 5-minute close price for {symbol_name}: {five_min_price}")
            return five_min_price
        else:
            print(f"Failed to fetch 5-minute data for {symbol_name}.")
            return None

    else:
        print("Invalid fetch type. Use 'current', 'start', or '5min'.")
        return None




eur = {'symbol': 'EURUSD', 'pip_size': 0.0001, 'threshold': 15}


start_price = fetch_price(eur, 'start')
current_price = fetch_price(eur, 'current')
print("symbol:", eur['symbol'], "Start Price:", start_price, "Current Price:", current_price, 'pip-difference', (current_price - start_price)/0.0001)

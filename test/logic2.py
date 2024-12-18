# import MetaTrader5 as mt5
from db import save_symbol_data, update_symbol_data, get_symbol_data


def calculate_pip_difference(symbol, start_price, current_price):
    """
    Calculates the pip difference between start_price and current_price.
    """
    pip_diff = start_price - current_price  # Retain order: start_price - current_price
    formatted_pip_difference = pip_diff / symbol['pip_size']  # Convert to pips using pip size

    # Round to two decimals, and then to the nearest whole number if very close
    rounded_pip_difference = round(formatted_pip_difference, 2)
    if abs(rounded_pip_difference - round(rounded_pip_difference)) < 0.01:
        rounded_pip_difference = round(rounded_pip_difference)

    return {'symbol': symbol['symbol'], 'pip_difference': rounded_pip_difference}


def check_and_hedge(symbol):
    """
    Checks if there are active positions for the given symbol.

    Args:
        symbol (str): The trading symbol to check.

    Returns:
        bool: True if positions exist, False otherwise.
    """
    if not symbol:
        return False
    trades = mt5.positions_get(symbol=symbol)
    return len(trades) > 0


def calculate_no_thresholds(symbol, start_price, current_price):
    """
    Calculate thresholds and determine hedging status based on pip differences.

    Args:
        symbol (dict): Symbol information, including 'symbol' and 'threshold'.
        start_price (float): The starting price for calculation.
        current_price (float): The current price for calculation.

    Returns:
        dict: Hedging details including direction, thresholds, and hedging status.
    """
    pip_data = calculate_pip_difference(symbol, start_price, current_price)
    pip_diff = pip_data['pip_difference']

    # If no difference, return neutral direction and no thresholds
    if pip_diff == 0:
        return {
            'symbol': symbol['symbol'],
            'hedging': False,
            'positive_hedging': False,
            'negative_hedging': False,
            'threshold_no': None,
            'pip_difference': pip_diff,
            'direction': "neutral"
        }

    # Determine direction and threshold number
    threshold_no = pip_diff / symbol['threshold'] if symbol['threshold'] != 0 else None
    direction = "positive" if pip_diff > 0 else "negative"

    # Check for active positions
    hedging = check_and_hedge(symbol['symbol'])

    # Initialize hedging flags
    positive_hedging = False
    negative_hedging = False

    # Determine hedging conditions
    if hedging and threshold_no is not None and 0 <= threshold_no <= 0.5:
        print(f"Positive hedging condition met at threshold_no: {threshold_no}")
        positive_hedging = True
    elif hedging and threshold_no is not None and -0.5 <= threshold_no < 0:
        print(f"Negative hedging condition met at threshold_no: {threshold_no}")
        negative_hedging = True

    # Update the overall hedging flag based on positive/negative hedging
    hedging = positive_hedging or negative_hedging

    return {
        'symbol': symbol['symbol'],
        'hedging': hedging,
        'positive_hedging': positive_hedging,
        'negative_hedging': negative_hedging,
        'threshold_no': round(threshold_no, 2) if threshold_no is not None else None,
        'pip_difference': pip_diff,
        'direction': direction
    }


def log_trade_decision(data):
    print("Trade Decision Data:")
    for key, value in data.items():
        print(f"{key}: {value}")


def decide_trade_and_thresholds(symbol, start_price, current_price):
    symbol_threshold_data = calculate_no_thresholds(symbol, start_price, current_price)

    # Classify thresholds based on direction
    direction = symbol_threshold_data['direction']
    threshold_no = symbol_threshold_data['threshold_no']

    # Determine thresholds
    first_positive_threshold = direction == "positive" and threshold_no is not None and abs(threshold_no) >= 1
    first_negative_threshold = direction == "negative" and threshold_no is not None and abs(threshold_no) >= 1
    second_positive_threshold = direction == "positive" and threshold_no is not None and abs(threshold_no) >= 2
    second_negative_threshold = direction == "negative" and threshold_no is not None and abs(threshold_no) >= 2

    # Prepare data for logging and analysis
    data = {
        'symbol': symbol['symbol'],
        'start_price': start_price,
        'current_price': current_price,
        'pip_difference': symbol_threshold_data['pip_difference'],
        'threshold_no': threshold_no,
        'first_positive_threshold': first_positive_threshold,
        'first_negative_threshold': first_negative_threshold,
        'second_positive_threshold': second_positive_threshold,
        'second_negative_threshold': second_negative_threshold,
        'positive_hedging': symbol_threshold_data['positive_hedging'],
        'negative_hedging': symbol_threshold_data['negative_hedging'],
        'direction': direction,
    }

    # Logging results for debugging and validation
    print("Trade Decision Data:")
    print(f"Symbol: {data['symbol']}")
    print(f"Start Price: {data['start_price']}, Current Price: {data['current_price']}")
    print(f"Pip Difference: {data['pip_difference']}")
    print(f"Threshold Number: {data['threshold_no']}")
    print(f"First Positive Threshold Reached: {data['first_positive_threshold']}")
    print(f"First Negative Threshold Reached: {data['first_negative_threshold']}")
    print(f"Second Positive Threshold Reached: {data['second_positive_threshold']}")
    print(f"Second Negative Threshold Reached: {data['second_negative_threshold']}")
    print(f"Positive Hedging Activated: {data['positive_hedging']}")
    print(f"Negative Hedging Activated: {data['negative_hedging']}")
    print(f"Direction: {data['direction']}")

    stored_data = get_symbol_data(symbol['symbol'])
    if stored_data != data:  # Update only if data has changed
        update_symbol_data(symbol['symbol'], data)

    # Logging for debugging
    log_trade_decision(data)
    return data


# Test the function
eur = {'symbol': 'EURUSD', 'pip_size': 0.0001, 'threshold': 15}
xag = {'symbol': 'XAGUSD', 'pip_size': 0.01, 'threshold': 20}
xau = {'symbol': 'XAUUSD', 'pip_size': 0.01, 'threshold': 700}

# Test with varying prices to validate logic
positive_prices = [
    1.1000,  # Neutral, no threshold crossed
    1.1015,  # Slight positive movement
    1.10075,  # Slight positive movement (hedging)
    1.1030,  # Threshold crossed (positive)
    1.1045,  # Negative threshold crossed,  # Second positive threshold crossed
]

negative_prices = [
    1.1000,  # Neutral, no threshold crossed
    1.0985,  # Slight negative movement
    1.0970,  # Threshold crossed (negative)
    1.0955,  # Positive threshold crossed,  # Second negative threshold crossed
]

xag_positive_prices = [
    30.20,
    30.40,
    30.60,
    30.80,
    31.00
]

xag_start_price = 30.00

xag_negative_prices = [
    29.80,
    29.60,
    29.40,
    29.20,
    29.00
]

xag_hedging_case = [
    29.60,  # Crosses the first negative threshold
    29.80,  # Returns toward 0.5 for positive hedging
    30.00,  # Neutral
    30.10,  # Approaches 0.5 for positive hedging
    29.50,  # Approaches -0.5 for negative hedging
    29.40,  # Second negative threshold crossed
]

# // Gold Case

xau_positive = [
    2600.00,
    2600.50,
    2601.00,
    2605.00,
    2602.5,
    2607.00,
    2610.10
]

xau_start = 2600.00

# Start price
start_price = 1.1000
#
# # Iterate through test prices
# for price in xag_positive_prices:
#     print("\nTesting with Positive Price:")
#     decide_trade_and_thresholds(xag, xag_start_price, price)
# print("======================================negative_prices======================================")
# for price in positive_prices:
#     print("\nTesting with Negative Price:")
#     decide_trade_and_thresholds(eur, start_price, price)

print("======================================gold positive prices======================================")
for price in xau_positive:
    print("\nTesting with Price:")
    decide_trade_and_thresholds(xau, xau_start, price)

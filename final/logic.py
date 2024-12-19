from db import save_symbol_data, update_symbol_data, get_symbol_data
from utils import get_open_positions

def calculate_pip_difference(symbol, start_price, current_price):
    pip_diff = start_price - current_price  # Retain order: start_price - current_price
    formatted_pip_difference = pip_diff / symbol['pip_size']  # Convert to pips using pip size

    # Round to two decimals, and then to the nearest whole number if very close
    rounded_pip_difference = round(formatted_pip_difference, 2)
    if abs(rounded_pip_difference - round(rounded_pip_difference)) < 0.01:
        rounded_pip_difference = round(rounded_pip_difference)

    return {'symbol': symbol['symbol'], 'pip_difference': rounded_pip_difference}


async def calculate_no_thresholds(symbol, start_price, current_price):

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
    direction = 'neutral'
    if pip_diff < 0:
        direction = "positive"
    elif pip_diff > 0:
        direction = "negative"

    # Check for active positions
    open_positions = await get_open_positions(symbol)

    # Initialize hedging flags
    hedging = False
    positive_hedging = False
    negative_hedging = False

    # No positions logic
    if open_positions['no_of_positions'] == 0:
        print(f"No open positions for {symbol['symbol']}. No hedging applied.")
        return {
            'symbol': symbol['symbol'],
            'hedging': False,
            'positive_hedging': False,
            'negative_hedging': False,
            'threshold_no': round(threshold_no, 2) if threshold_no is not None else None,
            'pip_difference': pip_diff,
            'direction': direction
        }

    # Determine hedging conditions for exactly two positions
    if open_positions['no_of_positions'] == 2 and threshold_no is not None:
        if 0 <= threshold_no <= 0.5:
            print(f"Positive hedging condition met at threshold_no: {threshold_no}")
            hedging = True
            positive_hedging = True
        elif -0.5 <= threshold_no < 0:
            print(f"Negative hedging condition met at threshold_no: {threshold_no}")
            hedging = True
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


async def decide_trade_and_thresholds(symbol, start_price, current_price):
    symbol_threshold_data = await calculate_no_thresholds(symbol, start_price, current_price)

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
    symbol_data = get_symbol_data(symbol['symbol'])
    if symbol_data is None:
        save_symbol_data(symbol['symbol'], data)
    else:
        update_symbol_data(symbol['symbol'], data)
    # log_trade_decision(data)
    return data
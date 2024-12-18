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


def calculate_no_thresholds(symbol, start_price, current_price):
    """
    Calculates the threshold number and direction based on pip difference.
    """
    # Calculate pip difference
    pip_data = calculate_pip_difference(symbol, start_price, current_price)
    pip_diff = pip_data['pip_difference']

    if pip_diff == 0:
        # If no difference, return None for threshold_no and "neutral" direction
        return {
            'symbol': symbol['symbol'],
            'threshold_no': None,
            'pip_difference': pip_diff,
            'direction': "neutral"
        }

    # Determine direction and threshold number
    if pip_diff > 0:  # Positive pip_diff means price decreased; direction is negative
        threshold_no = pip_diff / symbol['threshold']
        direction = "negative"
    elif pip_diff < 0:  # Negative pip_diff means price increased; direction is positive
        threshold_no = pip_diff / symbol['threshold']  # Keep threshold_no negative
        direction = "positive"
    else:
        threshold_no = 0
        direction = "neutral"

    return {
        'symbol': symbol['symbol'],
        'threshold_no': round(threshold_no, 2),
        'pip_difference': pip_diff,
        'direction': direction
    }


def decide_trade_and_thresholds(symbol, start_price, current_price):
    """
    Decides trade logic and checks threshold levels based on start_price and current_price.
    """
    # Calculate thresholds and direction
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
    print(f"Direction: {data['direction']}")

    return data


# Test the function
eur = {'symbol': 'EURUSD', 'pip_size': 0.0001, 'threshold': 15}
xag = {'symbol':'XAGUSD', 'pip_size': 0.01, 'threshold': 20}
xau = {'symbol':'XAUUSD', 'pip_size': 0.1, 'threshold': 1.5}

# Test with varying prices to validate logic
positive_prices = [
    1.1000,  # Neutral, no threshold crossed
    1.1015,  # Slight positive movement
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




# Start price
start_price = 1.1000

# Iterate through test prices
for price in xag_positive_prices:
    print("\nTesting with Positive Price:")
    decide_trade_and_thresholds(xag, xag_start_price, price)
print("======================================negative_prices======================================")
for price in xag_negative_prices:
    print("\nTesting with Negative Price:")
    decide_trade_and_thresholds(xag, xag_start_price, price)
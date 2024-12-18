from db import save_symbol_data, get_symbol_data, update_symbol_data, delete_symbol_data, clear_all_keys


def pip_difference(symbol, start_price, current_price):
    pip_diff = start_price - current_price
    formatted_pip_difference = pip_diff / symbol['pip_size']
    return {'symbol': symbol['symbol'], 'pip_difference': round(formatted_pip_difference, 2)}


def threshold_no(symbol, pip_diff):
    if pip_diff == 0:
        return {'symbol': symbol['symbol'], 'threshold_no': None}
    threshold_val = pip_diff / symbol['threshold']
    return {'symbol': symbol['symbol'], 'threshold_no': round(threshold_val, 2)}


def check_threshold_levels(threshold_no):
    thresholds_reached = 0
    if threshold_no is None or threshold_no == 0:
        return {'thresholds_reached': thresholds_reached}

    if threshold_no > 0:
        thresholds_reached = int(threshold_no)
    elif threshold_no < 0:
        thresholds_reached = abs(int(threshold_no))

    return {'thresholds_reached': thresholds_reached}


def combine_logic(symbol, start_price, current_price):
    data = pip_difference(symbol, start_price, current_price)
    threshold_data = threshold_no(symbol, data['pip_difference'])
    thresholds_info = check_threshold_levels(threshold_data['threshold_no'])

    combined = {
        'symbol': data['symbol'],
        'pip_difference': data['pip_difference'],
        'threshold_no': threshold_data['threshold_no'],
        'thresholds_reached': thresholds_info['thresholds_reached']
    }
    return combined


def decide_trade(symbol, start_price, current_price):
    """
    Based on the current price, decide whether to place a trade, hedge, or close trades.
    Also, track threshold boolean, threshold_reached_at, and direction.
    """
    result = combine_logic(symbol, start_price, current_price)
    symbol_name = result['symbol']
    threshold_no_val = result['threshold_no']
    thresholds_reached = result['thresholds_reached']
    pip_diff = result['pip_difference']

    # Determine direction
    # If pip_difference < 0, direction = "positive"
    # If pip_difference > 0, direction = "negative"
    direction = "positive" if pip_diff < 0 else "negative" if pip_diff > 0 else "neutral"

    # Retrieve or initialize state from DB
    current_data = get_symbol_data(symbol_name)
    if current_data is None:
        # Initialize fresh state with new fields
        current_data = {
            'symbol': symbol_name,
            'threshold_reached': False,
            'threshold_reached_at': None,
            'threshold': False,
            'positive_threshold': False,
            'negative_threshold': False,
            'trades_placed': False,
            'hedging': False,
            'direction': direction,
            'thresholds_no': threshold_no_val,
            'start_price': start_price,
            'current_price': current_price
        }
        save_symbol_data(symbol_name, current_data)
    else:
        # Reinitialize to a clean state with only known keys
        current_data = {
            'symbol': symbol_name,
            'threshold_reached': current_data.get('threshold_reached', False),
            'threshold_reached_at': current_data.get('threshold_reached_at', None),
            'threshold': current_data.get('threshold', False),
            'positive_threshold': current_data.get('positive_threshold', False),
            'negative_threshold': current_data.get('negative_threshold', False),
            'trades_placed': current_data.get('trades_placed', False),
            'hedging': current_data.get('hedging', False),
            'direction': direction,  # Always update direction
            'thresholds_no': threshold_no_val,
            'start_price': start_price,
            'current_price': current_price
        }

    # Threshold logic
    if threshold_no_val is not None:
        # Check if we've crossed first threshold (≥1 or ≤-1)
        if abs(threshold_no_val) >= 1 and not current_data['threshold']:
            # We just reached threshold
            current_data['threshold'] = True
            current_data['threshold_reached'] = True
            current_data['threshold_reached_at'] = current_price

            # Based on direction, set positive or negative threshold
            if direction == "positive":
                current_data['positive_threshold'] = True
            elif direction == "negative":
                current_data['negative_threshold'] = True

        # Positive threshold scenario
        if threshold_no_val >= 1:
            if current_data['threshold_reached'] and not current_data['trades_placed']:
                # If within 1 to 1.2 range, place trade
                if 1 <= threshold_no_val <= 1.2:
                    print("Placing trade at first positive threshold range.")
                    current_data['trades_placed'] = True

        # Negative threshold scenario
        elif threshold_no_val <= -1:
            if current_data['threshold_reached'] and not current_data['trades_placed']:
                if -1.2 <= threshold_no_val <= -1:
                    print("Placing trade at first negative threshold range.")
                    current_data['trades_placed'] = True

        # Hedging scenario: threshold reached, trade placed, not hedging yet, back towards ±0.5
        if current_data['threshold_reached'] and current_data['trades_placed'] and not current_data['hedging']:
            # From positive side to 0.5
            if 0 <= threshold_no_val <= 0.5:
                print("Opposite trade time (hedging) - threshold returned to 0.5 for positive side.")
                current_data['hedging'] = True
            # From negative side to -0.5
            elif -0.5 <= threshold_no_val < 0:
                print("Opposite trade time (hedging) - threshold returned to -0.5 for negative side.")
                current_data['hedging'] = True

        # Second threshold scenario: close trades
        if thresholds_reached >= 2:
            print("Second threshold reached or exceeded, closing trades.")
            current_data['trades_placed'] = False
            current_data['hedging'] = False

    # Save the updated state back to DB
    update_symbol_data(symbol_name, current_data)

    return result, current_data


def decide_trade_logic(symbol, start_price, current_price):
    obtained_pip_difference = pip_difference(symbol, start_price, current_price)
    print(f"{symbol['symbol']} at {current_price} - pip-difference:{obtained_pip_difference} - threshold_no:{threshold_no(symbol, obtained_pip_difference['pip_difference'])} - thresholds_reached:{check_threshold_levels(threshold_no(symbol, obtained_pip_difference['pip_difference'])['threshold_no'])}")


# Example usage
if __name__ == "__main__":
    eur = {'symbol': 'EURUSD', 'pip_size': 0.0001, 'threshold': 15}
    start_price = 1.0000
    test_prices = [
       1.0000,
       1.0013,
       1.0020,
       1.0025,
       1.0030,
        1.0035,
        1.0040,
        1.0045,
        1.0050,
        1.0055,
        1.0060,
    ]

    for p in test_prices:
        decide_trade_logic(eur, 1.0015, p)
        # result, state = decide_trade_logic(eur, start_price, p)
        # print("Current Price:", p)
        # print("Result:", result)
        # print("State:", state)
        # print("-" * 50)

    # eurdb = get_symbol_data('EURUSD')
    # print("db", eurdb)
# clear_all_keys()

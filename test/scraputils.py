def save_trade_type(symbol, pip_difference, start_price, current_price):
    threshold_data = threshold_no(symbol, pip_difference)
    dataKey = get_symbol_data(symbol['symbol'])
    if dataKey is None:
        data = {
            'symbol': symbol['symbol'],
            'pip_difference': pip_difference,
            'start_price': start_price,
            'current_price': current_price,
            'threshold': False,
            'threshold_reached_at': None,
            'threshold_no': threshold_data['threshold_no'],
            'positive_threshold': False,
            'positive_threshold_reached_at': None,
            'negative_threshold': False,
            'negative_threshold_reached_at': None,
            'hedging': False,
            'hedging_reached_at': None,
            'hedging_no': None
        }
        save_symbol_data(symbol['symbol'], data)

    if threshold_data['threshold_no'] >= 1:
        data['threshold'] = True
        data['threshold_reached_at'] = current_price
        data['negative_threshold'] = True
        data['negative_threshold_reached_at'] = current_price
        data['threshold_no'] = threshold_data['threshold_no']
        update_symbol_data(symbol['symbol'], data)
        if threshold_data['threshold_no'] >= 2:
            data['threshold_no'] = threshold_data['threshold_no']
            update_symbol_data(symbol['symbol'], data)
        if threshold_data['threshold_no'] <= 0.5:
            data['hedging'] = True
            data['hedging_reached_at'] = current_price
            update_symbol_data(symbol['symbol'], data)
    elif threshold_data['threshold_no'] <= -1:
        data['threshold'] = True
        data['threshold_reached_at'] = current_price
        data['positive_threshold'] = True
        data['positive_threshold_reached_at'] = current_price
        data['threshold_no'] = threshold_data['threshold_no']
        update_symbol_data(symbol['symbol'], data)
        if threshold_data['threshold_no'] <= -2:
            data['threshold_no'] = threshold_data['threshold_no']
            update_symbol_data(symbol['symbol'], data)
        if threshold_data['threshold_no'] >= -0.5:
            data['hedging'] = True
            data['hedging_reached_at'] = current_price
            update_symbol_data(symbol['symbol'], data)


def decide_trade(symbol):
    symbol_name = symbol['symbol']
    data = get_symbol_data(symbol_name)


def assemble_logic(symbol, start_price, current_price, decide):
    data = pip_difference(symbol, start_price, current_price)
    threshold_data = threshold_no(symbol, data['pip_difference'])
    if decide:
        decide_trade(symbol, start_price, current_price)

    return {
        'symbol': symbol['symbol'],
        'pip_difference': data['pip_difference'],
        'threshold_no': threshold_data['threshold_no']
    }

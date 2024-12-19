import MetaTrader5 as mt5
from notifications import send_discord_message_type
import asyncio

TRADE_LIMIT = 2

async def place_order(symbol, action, lot, hedge):
    # Initialize MetaTrader5
    if not mt5.initialize():
        message = "MetaTrader5 initialization failed."
        await send_discord_message_type(message, "error", True)
        print(message)
        return

    try:
        # Extract the symbol string
        symbol_name = symbol['symbol']

        # Check open positions
        open_positions = mt5.positions_get(symbol=symbol_name)
        current_open_trades = len(open_positions) if open_positions else 0

        # Check trade limit based on hedging
        if not hedge and current_open_trades >= TRADE_LIMIT:
            message = f"Trade limit reached for {symbol_name}. No trade placed."
            await send_discord_message_type(message, "error", True)
            print(message)
            return
        elif hedge and current_open_trades >= TRADE_LIMIT * 2:
            message = f"Hedging limit reached for {symbol_name}. No trade placed."
            await send_discord_message_type(message, "error", True)
            print(message)
            return

        # Determine trade action
        trade_action = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

        # Get current price for the trade
        symbol_info = mt5.symbol_info_tick(symbol_name)
        if not symbol_info:
            message = f"Symbol info not found for {symbol_name}."
            await send_discord_message_type(message, "error", True)
            print(message)
            return

        price = symbol_info.bid if action == 'buy' else symbol_info.ask
        deviation = 20

        # Prepare the order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": lot,
            "type": trade_action,
            "price": price,
            "deviation": deviation,
            "magic": 234000,
            "comment": f"Python script open {action}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        # Send the order
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            message = f"Order placed successfully for {symbol_name}. Result: {result}"
            await send_discord_message_type(message, "trade", True)
            print("Order send result:", result)
        else:
            message = f"Order send failed for {symbol_name}: {result.comment}"
            await send_discord_message_type(message, "error", True)
            print(message)

    finally:
        # Always shut down MT5 connection
        mt5.shutdown()


async def close_trades_by_symbol(symbol):
    if not mt5.initialize():
        message = "MetaTrader5 initialization failed."
        await send_discord_message_type(message, "error", True)
        print(message)
        return

    symbol_name = symbol['symbol']
    open_positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol_name)

    if not open_positions:
        print(f"No open positions for {symbol_name}. {open_positions}")
        return

    for position in open_positions:
        ticket = position.ticket
        lot = position.volume
        trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        symbol_info = await asyncio.to_thread(mt5.symbol_info, symbol_name)

        if symbol_info is None:
            print(f"Symbol {symbol_name} not found.")
            continue

        price = symbol_info.bid if trade_type == mt5.ORDER_TYPE_SELL else symbol_info.ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": lot,
            "type": trade_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Closing trade by script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = await asyncio.to_thread(mt5.order_send, close_request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            message = f"Trade closed successfully for {symbol_name}. Result: {result}"
            await send_discord_message_type(message, "trade", True)
            print("Order close result:", result)
        elif result.retcode == mt5.TRADE_RETCODE_REJECT:
            message = f"Trade close rejected for {symbol_name}: {result.comment}"
            await send_discord_message_type(message, "error", True)
            print(message)
        else:
            # Handle other error conditions if needed
            message = f"Trade close failed for {symbol_name}. Retcode: {result.retcode} Comment: {result.comment}"
            await send_discord_message_type(message, "error", True)
            print(message)
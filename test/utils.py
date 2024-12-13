import asyncio
import MetaTrader5 as mt5
import logging
from notifications import send_limited_message, send_discord_message_async
from datetime import datetime
from storage_state import save_symbol_data


async def log_error_and_notify(message):
    logging.error(message)
    await send_discord_message_async(message)


async def connect_mt5():
    """Asynchronously initialize and log in to MetaTrader 5."""
    initialized = await asyncio.to_thread(mt5.initialize)
    if not initialized:
        print("Failed to initialize MetaTrader5")
        return False

    login = 213171528  # Replace with actual login
    password = "AHe@Yps3"  # Replace with actual password
    server = "OctaFX-Demo"  # Replace with actual server

    authorized = await asyncio.to_thread(mt5.login, login, password, server)
    if authorized:
        account = await asyncio.to_thread(mt5.account_info)
        balance = account.balance
        save_symbol_data("account", account)
        print(f"Successfully logged into account {login} on server {server}")
        print(f"balance {balance}")
    if not authorized:
        print(f"Login failed for account {login}")
        return False


    return True


async def get_open_positions(symbol):
    """Fetch open positions for a symbol and return position details consistently."""
    symbol_name = symbol["symbol"]
    positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol_name)

    open_positions = {
        "positions_exist": len(positions) > 0,
        "no_of_positions": len(positions) if positions else 0
    }

    if not positions:
        await send_limited_message(symbol_name, f"No positions exist for {symbol_name} at {datetime.now()}")

    return open_positions
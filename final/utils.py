import MetaTrader5 as mt5
import logging
from notifications import send_limited_message, send_discord_message_async, send_discord_message_type
from datetime import datetime
from db import save_symbol_data
import asyncio

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
    if not mt5.initialize():
        message = f"MetaTrader5 initialization failed at {datetime.now()}"
        await send_discord_message_type(message, "error", True)
    else:
        """Fetch open positions for a symbol and return position details consistently."""
        symbol_name = symbol["symbol"]
        try:
            positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol_name)
            print("positions", positions)

            if positions is None:
                message = f"Error fetching positions for {symbol_name} at {datetime.now()}"
                await send_discord_message_type(message, "error", True)
                return {
                    "positions_exist": False,
                    "no_of_positions": 0
                }

            if not positions:
                message = f"No positions exist for {symbol_name} at {datetime.now()}"
                await send_discord_message_type(message, "error", True)

            open_positions = {
                "positions_exist": len(positions) > 0,
                "no_of_positions": len(positions) if positions else 0
            }
            return open_positions

        except Exception as e:
            message = f"An error occurred while fetching positions for {symbol_name}: {e}"
            await send_discord_message_type(message, "error", True)
            return {
                "positions_exist": False,
                "no_of_positions": 0
            }

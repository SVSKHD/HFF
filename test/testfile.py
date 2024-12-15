from config import symbols_config
import asyncio

from db import clear_all_keys, get_symbol_data
from trade_place import place_order, close_trades_by_symbol  # Ensure this file is properly importing close_trades_by_symbol

# async def main():
#     tasks = [
#         close_trades_by_symbol(symbol) for symbol in symbols_config
#     ]
#     await asyncio.gather(*tasks)
#
# if __name__ == "__main__":
#     asyncio.run(main())

btc=get_symbol_data('BTCUSD')
print(btc)
usd=get_symbol_data('EURUSD')
print(usd)
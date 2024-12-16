from db import get_symbol_data, clear_all_keys, save_symbol_data, update_symbol_data

# print(get_symbol_data("EURUSD"))
# clear_all_keys()


save_symbol_data("EURUSD", {"symbol": "EURUSD", "pip_size": 0.0001, "threshold": 0.1})
print(get_symbol_data("EURUSD"))
update_symbol_data("EURUSD", {"threshold": 0.2})
print(get_symbol_data("EURUSD"))
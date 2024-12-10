import redis
import json
import zlib
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=['settings.toml'],
    environments=True,
)

# Redis connection details
redis_url = settings.DATABASE_URL

try:
    # Connect to Redis
    redis_client = redis.from_url(redis_url)
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    redis_client = None


# Compress data before saving to Redis
def compress_data(data):
    json_data = json.dumps(data)
    compressed_data = zlib.compress(json_data.encode('utf-8'))
    return compressed_data


# Decompress data after retrieving from Redis
def decompress_data(compressed_data):
    json_data = zlib.decompress(compressed_data).decode('utf-8')
    data = json.loads(json_data)
    return data


# Save data to Redis
def save_symbol_data(key, symbol_data):
    if redis_client:
        try:
            existing_data = get_symbol_data(key)
            if existing_data and isinstance(existing_data, dict):
                existing_data.update(symbol_data)
                compressed_data = compress_data(existing_data)
            else:
                compressed_data = compress_data(symbol_data)
            redis_client.set(key, compressed_data)
            print(f"Compressed data saved under key: {key}")
        except Exception as e:
            print(f"Error saving data to Redis: {e}")
    else:
        print("Redis client is not connected.")


# Retrieve data from Redis
def get_symbol_data(key):
    if redis_client:
        try:
            compressed_data = redis_client.get(key)
            if compressed_data:
                data = decompress_data(compressed_data)
                return data
            print(f"No data found for key: {key}")
            return None
        except Exception as e:
            print(f"Error retrieving data from Redis: {e}")
            return None
    else:
        print("Redis client is not connected.")
        return None


# Update data in Redis
def update_symbol_data(key, new_data):
    if redis_client:
        try:
            existing_data = get_symbol_data(key)
            if existing_data and isinstance(existing_data, dict):
                existing_data.update(new_data)
                save_symbol_data(key, existing_data)
                print(f"Data for key '{key}' updated successfully.")
            else:
                print(f"No existing data found for key: {key}")
        except Exception as e:
            print(f"Error updating data in Redis: {e}")
    else:
        print("Redis client is not connected.")


# Delete data from Redis
def delete_symbol_data(key):
    if redis_client:
        try:
            result = redis_client.delete(key)
            if result:
                print(f"Key '{key}' deleted successfully.")
            else:
                print(f"Key '{key}' does not exist.")
        except Exception as e:
            print(f"Error deleting data from Redis: {e}")
    else:
        print("Redis client is not connected.")


def save_or_update_start_trade(value: bool):
    if redis_client:
        try:
            compressed_data = compress_data(value)
            redis_client.set("start_trade", compressed_data)
            print(f"Start trade set to {value}")
        except Exception as e:
            print(f"Error saving or updating start_trade: {e}")
    else:
        print("Redis client is not connected.")


def get_start_trade():
    if redis_client:
        try:
            compressed_data = redis_client.get("start_trade")
            if compressed_data:
                start_trade = decompress_data(compressed_data)
                return start_trade
            else:
                print("No start_trade data found.")
                return None
        except Exception as e:
            print(f"Error retrieving start_trade: {e}")
            return None
    else:
        print("Redis client is not connected.")
        return None


# Clear all keys in Redis
def clear_all_keys():
    if redis_client:
        try:
            redis_client.flushdb()
            print("All keys cleared from Redis.")
        except Exception as e:
            print(f"Error clearing all keys from Redis: {e}")
    else:
        print("Redis client is not connected.")
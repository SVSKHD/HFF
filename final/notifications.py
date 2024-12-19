import aiohttp
from datetime import datetime
import logging
from dynaconf import Dynaconf

# Load settings
settings = Dynaconf(
    settings_files=['settings.toml'],
    environments=True,
)

general_url = settings.GENERAL_DISCORD
trade_url = settings.TRADE_DISCORD
error_url = settings.ERROR_DISCORD
scheduler_url = settings.SCHEDULER_DISCORD

# Rate limiting configuration
last_message_time = {}
MESSAGE_INTERVAL = 60  # seconds

async def send_discord_message_async(webhook_url, message):
    data = {"content": message}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=data) as response:
                if response.status == 204:
                    print("Message sent successfully!")
                else:
                    print(f"Failed to send message: {response.status}, {await response.text()}")
        except Exception as e:
            print(f"Error sending message: {e}")

async def send_limited_message(webhook_url, message):
    current_time = datetime.now()
    last_time = last_message_time.get(webhook_url)
    if last_time is None or (current_time - last_time).total_seconds() > MESSAGE_INTERVAL:
        logging.info(f"Sending message: {message}")
        await send_discord_message_async(webhook_url, message)
        last_message_time[webhook_url] = current_time
    else:
        logging.info("Message rate-limited; not sent.")

async def send_discord_message_type(message, type, limited=False):
    webhook_url = None
    if type == "trade":
        webhook_url = trade_url
    elif type == "general":
        webhook_url = general_url
    elif type == "error":
        webhook_url = error_url
    elif type == "scheduler":
        webhook_url = scheduler_url
    else:
        print(f"Unsupported message type: {type}")
        return  # Exit if the type is unsupported

    if not webhook_url:
        print("Webhook URL is not defined.")
        return

    if limited:
        # Use rate-limiting if limited is True
        await send_limited_message(webhook_url, message)
    else:
        # Send message directly if not limited
        await send_discord_message_async(webhook_url, message)
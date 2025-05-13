import logging
import asyncio
import os
import signal
import time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramNetworkError
from handlers.start import register_start_handlers
from handlers.global_stats import register_global_stats_handlers
from handlers.top_coins import register_top_coins_handlers
from handlers.search import register_search_handlers
from handlers.exchanges import register_exchanges_handlers
from handlers.favorites import register_favorites_handlers
from handlers.help import register_help_handlers
from handlers.coin_details import register_coin_details_handlers


logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help"),
        BotCommand(command="/global", description="Global crypto stats"),
        BotCommand(command="/top", description="View top cryptocurrencies"),
    ]
    # Retry mechanism for network issues
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            await bot.set_my_commands(commands)
            return
        except TelegramNetworkError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Network error setting commands (attempt {attempt+1}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logging.error(f"Failed to set commands after {max_retries} attempts: {e}")
                # Continue without setting commands
                return


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    
    # Create storage and dispatcher
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register all handlers
    register_start_handlers(dp)
    register_global_stats_handlers(dp)
    register_top_coins_handlers(dp)
    register_search_handlers(dp)
    register_exchanges_handlers(dp)
    register_favorites_handlers(dp)
    register_help_handlers(dp)
    register_coin_details_handlers(dp)
    
    # Set bot commands with error handling
    try:
        await set_commands(bot)
    except Exception as e:
        logging.error(f"Error setting commands: {e}")
        # Continue without commands if setting fails
    
    # Start polling with retry mechanism
    max_polling_retries = 5
    polling_retry_delay = 5  # seconds
    
    for attempt in range(max_polling_retries):
        try:
            logging.info("Bot started!")
            # Clear previous webhook if any to prevent conflict
            await bot.delete_webhook(drop_pending_updates=True)
            
            # Start polling with proper error handling
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
            break  # If polling succeeds, exit the retry loop
            
        except TelegramNetworkError as e:
            if attempt < max_polling_retries - 1:
                logging.warning(f"Network error during polling (attempt {attempt+1}/{max_polling_retries}): {e}")
                await asyncio.sleep(polling_retry_delay)
                polling_retry_delay *= 1.5  # Gradually increase delay
            else:
                logging.error(f"Failed to start polling after {max_polling_retries} attempts: {e}")
                raise  # Re-raise the exception if all retries fail
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
        finally:
            if attempt == max_polling_retries - 1:  # Only close on last attempt
                logging.info("Bot stopping...")
                await dp.storage.close()
                await bot.session.close()
                logging.info("Bot stopped!")


def signal_handler(sig, frame):
    """Handle termination signals properly"""
    logging.info(f"Received signal {sig}, shutting down...")
    raise KeyboardInterrupt


if __name__ == '__main__':
    # Set up signal handlers for proper shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped via keyboard interrupt!")
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}")
        # Add a small delay before exiting to ensure logs are written
        time.sleep(1)

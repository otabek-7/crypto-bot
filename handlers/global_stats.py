from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from services.coinlore_api import CoinloreAPI
from keyboards.main_menu import get_main_menu_keyboard


async def global_stats_handler(message: types.Message, state: FSMContext):
    """
    Handler for the Global Stats button.
    Shows global cryptocurrency market statistics.
    """
    # Show typing status while fetching data
    await message.chat.do("typing")
    
    # Get global stats from API
    global_stats = await CoinloreAPI.get_global_stats()
    
    if not global_stats or len(global_stats) == 0:
        await message.answer(
            "❌ Sorry, couldn't fetch global cryptocurrency statistics. Please try again later.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Extract data from response (first item contains global stats)
    stats = global_stats[0] if isinstance(global_stats, list) else global_stats
    
    # Format the statistics message
    stats_text = (
        "🌐 *Global Cryptocurrency Statistics*\n\n"
        f"💰 *Total Market Cap:* ${format_number(stats.get('total_mcap', 0))} USD\n"
        f"💵 *Total Volume (24h):* ${format_number(stats.get('total_volume', 0))} USD\n\n"
        f"📊 *Active Markets:* {format_number(stats.get('active_markets', 0))}\n"
        f"🪙 *Active Cryptocurrencies:* {format_number(stats.get('active_cryptocurrencies', 0))}\n\n"
        f"🔷 *BTC Dominance:* {stats.get('btc_d', 0)}%\n"
        f"🔹 *ETH Dominance:* {stats.get('eth_d', 0)}%\n\n"
        f"📈 *Market Cap Change (24h):* {stats.get('mcap_change', 0)}%\n"
        f"⏱ *Last Updated:* {stats.get('time', '')}"
    )
    
    await message.answer(
        stats_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )


def format_number(num):
    """Format large numbers for better readability"""
    if isinstance(num, str):
        try:
            num = float(num)
        except ValueError:
            return num
    
    if isinstance(num, (int, float)):
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return f"{num:.2f}"
    return str(num)


def register_global_stats_handlers(dp):
    """
    Register handlers for global statistics
    """
    router = Router()
    router.message.register(global_stats_handler, F.text == "🌐 Global Stats")
    dp.include_router(router)
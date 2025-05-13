from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import get_main_menu_keyboard
from services.coinlore_api import CoinloreAPI


async def help_command(message: types.Message, state: FSMContext):
    """Handle the Help button press or /help command"""
    
    # Get global market stats to enhance the help message
    global_stats = await CoinloreAPI.get_global_stats()
    
    market_info = ""
    if global_stats and len(global_stats) > 0:
        stats = global_stats[0]
        
        total_coins = stats.get('coins_count', 'N/A')
        active_markets = stats.get('active_markets', 'N/A')
        total_mcap = float(stats.get('total_mcap', 0))
        total_volume = float(stats.get('total_volume', 0))
        
        # Format market cap and volume with commas
        total_mcap_formatted = f"${total_mcap:,.0f}" if total_mcap else "N/A"
        total_volume_formatted = f"${total_volume:,.0f}" if total_volume else "N/A"
        
        market_info = (
            "📊 Current Market Overview:\n"
            f"• Total Cryptocurrencies: {total_coins}\n"
            f"• Active Markets: {active_markets}\n"
            f"• Total Market Cap: {total_mcap_formatted}\n"
            f"• 24h Trading Volume: {total_volume_formatted}\n\n"
        )
    
    help_text = (
        "ℹ️ *Crypto Assistant Bot Help*\n\n"
        f"{market_info}"
        "*Available Features:*\n\n"
        "🌐 *Global Stats* - View overall cryptocurrency market statistics including total market cap, volume, and BTC dominance\n\n"
        "💹 *Top Cryptos* - Browse the top cryptocurrencies by market cap with current prices and 24h changes\n\n"
        "🔍 *Search Coin* - Find specific cryptocurrencies by name or symbol, view detailed information and price data\n\n"
        "📊 *Exchanges* - View top cryptocurrency exchanges ranked by trading volume\n\n"
        "⭐ *Favorites* - Save and access your favorite cryptocurrencies for quick monitoring\n\n"
        "*Commands:*\n"
        "/start - Restart the bot\n"
        "/help - Show this help message\n"
        "/global - Show global statistics\n"
        "/top - Show top cryptocurrencies\n\n"
        "*Data Source:*\n"
        "All cryptocurrency data is provided by CoinLore API"
    )
    
    await message.answer(
        help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


def register_help_handlers(dp):
    """Register all help related handlers"""
    router = Router()
    
    # Button handler for "Help"
    router.message.register(help_command, F.text == "ℹ️ Help")
    
    # Command handler for /help
    router.message.register(help_command, Command(commands=["help"]))
    
    dp.include_router(router)

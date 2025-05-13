from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu import get_main_menu_keyboard
from services.coinlore_api import CoinloreAPI


async def coin_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """Handle callback when a user clicks on a specific coin"""
    
    # Extract coin_id from callback data (format: coin_ID)
    coin_id = callback.data.split('_')[1]
    
    # Get coin data from API
    coin_data = await CoinloreAPI.get_ticker(coin_id)
    
    if not coin_data:
        await callback.answer("Could not retrieve coin data. Please try again.")
        return
    
    # Get user data to check if this coin is in favorites
    user_data = await state.get_data()
    favorites = user_data.get("favorites", [])
    is_favorite = coin_id in favorites
    
    # Create detailed coin info message
    name = coin_data.get('name', 'Unknown')
    symbol = coin_data.get('symbol', '')
    rank = coin_data.get('rank', 'N/A')
    price_usd = coin_data.get('price_usd', 'N/A')
    
    # Format the numbers nicely
    if price_usd != 'N/A':
        price_usd = f"${float(price_usd):,.6f}" if float(price_usd) < 1 else f"${float(price_usd):,.2f}"
    
    market_cap = float(coin_data.get('market_cap_usd', 0))
    market_cap_formatted = f"${market_cap:,.0f}" if market_cap else "N/A"
    
    volume_24h = float(coin_data.get('volume24', 0))
    volume_formatted = f"${volume_24h:,.0f}" if volume_24h else "N/A"
    
    change_1h = coin_data.get('percent_change_1h', 'N/A')
    change_24h = coin_data.get('percent_change_24h', 'N/A')
    change_7d = coin_data.get('percent_change_7d', 'N/A')
    
    # Add emojis for changes
    change_1h_emoji = "🟢" if change_1h != 'N/A' and float(change_1h) > 0 else "🔴" if change_1h != 'N/A' and float(change_1h) < 0 else "⚪"
    change_24h_emoji = "🟢" if change_24h != 'N/A' and float(change_24h) > 0 else "🔴" if change_24h != 'N/A' and float(change_24h) < 0 else "⚪"
    change_7d_emoji = "🟢" if change_7d != 'N/A' and float(change_7d) > 0 else "🔴" if change_7d != 'N/A' and float(change_7d) < 0 else "⚪"
    
    message_text = (
        f"*{name} ({symbol})*  Rank #{rank}\n\n"
        f"*Price:* {price_usd}\n"
        f"*Market Cap:* {market_cap_formatted}\n"
        f"*24h Volume:* {volume_formatted}\n\n"
        f"*Change 1h:* {change_1h_emoji} {change_1h}%\n"
        f"*Change 24h:* {change_24h_emoji} {change_24h}%\n"
        f"*Change 7d:* {change_7d_emoji} {change_7d}%\n\n"
        f"*Last Updated:* {coin_data.get('last_updated', 'N/A')}"
    )
    
    # Create inline keyboard with options
    buttons = []
    
    # Add/Remove favorite button
    if is_favorite:
        buttons.append([InlineKeyboardButton(
            text="⭐ Remove from Favorites",
            callback_data=f"rm_fav_{coin_id}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="⭐ Add to Favorites",
            callback_data=f"add_fav_{coin_id}"
        )])
    
    # Add button to markets and website
    url_buttons = []
    
    # Add website button if available
    # Note: CoinLore API doesn't provide website URLs in ticker data
    # This would need additional API calls or a predefined list
    
    url_buttons.append(InlineKeyboardButton(
        text="🔍 View on CoinLore",
        url=f"https://www.coinlore.com/coin/{coin_data.get('nameid', name.lower())}"
    ))
    
    buttons.append(url_buttons)
    
    # Add back button
    buttons.append([InlineKeyboardButton(
        text="🔙 Back",
        callback_data="back_to_menu"
    )])
    
    # Create the keyboard
    coin_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # Edit the message with coin details
    try:
        await callback.message.edit_text(
            message_text,
            reply_markup=coin_keyboard,
            parse_mode="Markdown"
        )
    except Exception:
        # If can't edit (might be too old), send a new message
        await callback.message.answer(
            message_text,
            reply_markup=coin_keyboard,
            parse_mode="Markdown"
        )
    
    await callback.answer()


async def back_to_menu_callback(callback: types.CallbackQuery):
    """Handle back to menu button"""
    await callback.answer("Returning to main menu")
    await callback.message.delete()


def register_coin_details_handlers(dp):
    """Register all coin detail related handlers"""
    router = Router()
    
    # Coin detail handler
    router.callback_query.register(coin_callback_handler, F.data.startswith("coin_"))
    
    # Back to menu handler
    router.callback_query.register(back_to_menu_callback, F.data == "back_to_menu")
    
    dp.include_router(router)

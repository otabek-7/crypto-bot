from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu import get_main_menu_keyboard
from services.coinlore_api import CoinloreAPI


async def favorites_command(message: types.Message, state: FSMContext):
    """Handle the Favorites button press"""
    
    # Get user data from state to retrieve favorites
    user_data = await state.get_data()
    favorites = user_data.get("favorites", [])
    
    if not favorites:
        await message.answer(
            "⭐ You don't have any favorite cryptocurrencies yet.\n\n"
            "To add favorites, search for a coin using the '🔍 Search Coin' button "
            "or view top cryptocurrencies, then select 'Add to Favorites'.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Get current data for all favorite coins
    favorite_coins = []
    
    for coin_id in favorites:
        coin_data = await CoinloreAPI.get_ticker(coin_id)
        if coin_data:
            favorite_coins.append(coin_data)
    
    if favorite_coins:
        # Sort favorites by market cap
        sorted_favorites = sorted(favorite_coins, key=lambda x: float(x.get('market_cap_usd', 0)), reverse=True)
        
        # Create message with favorite coins
        message_text = "⭐ Your Favorite Cryptocurrencies\n\n"
        
        buttons = []
        
        for coin in sorted_favorites:
            coin_id = coin.get('id')
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '')
            price = coin.get('price_usd', 'N/A')
            
            # Format price
            price_formatted = f"${float(price):,.2f}" if price and price != 'N/A' else "N/A"
            
            # Calculate 24h change
            change_24h = coin.get('percent_change_24h', 0)
            change_emoji = "🟢" if float(change_24h) > 0 else "🔴" if float(change_24h) < 0 else "⚪"
            
            message_text += f"*{name} ({symbol})*\n"
            message_text += f"Price: {price_formatted}\n"
            message_text += f"24h Change: {change_emoji} {change_24h}%\n\n"
            
            # Add button for this coin
            buttons.append([InlineKeyboardButton(
                text=f"{name} ({symbol})",
                callback_data=f"coin_{coin_id}"
            )])
        
        # Add button to remove all favorites
        buttons.append([InlineKeyboardButton(
            text="🗑️ Clear All Favorites",
            callback_data="clear_favorites"
        )])
        
        # Create keyboard with buttons
        favorites_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.answer(
            message_text,
            reply_markup=favorites_keyboard,
            parse_mode="Markdown"
        )
        
        # Return to main menu
        await message.answer(
            "What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "⚠️ I couldn't retrieve data for your favorite coins. Please try again later.",
            reply_markup=get_main_menu_keyboard()
        )


async def add_favorite_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle adding a coin to favorites"""
    # The callback data format is expected to be "add_fav_COIN_ID"
    coin_id = callback.data.split("_")[2]
    
    # Get current favorites
    user_data = await state.get_data()
    favorites = user_data.get("favorites", [])
    
    if coin_id in favorites:
        await callback.answer("This coin is already in your favorites!")
        return
    
    # Add to favorites
    favorites.append(coin_id)
    await state.update_data(favorites=favorites)
    
    await callback.answer("Added to favorites!")


async def remove_favorite_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle removing a coin from favorites"""
    # The callback data format is expected to be "rm_fav_COIN_ID"
    coin_id = callback.data.split("_")[2]
    
    # Get current favorites
    user_data = await state.get_data()
    favorites = user_data.get("favorites", [])
    
    if coin_id in favorites:
        favorites.remove(coin_id)
        await state.update_data(favorites=favorites)
        await callback.answer("Removed from favorites!")
    else:
        await callback.answer("This coin is not in your favorites!")


async def clear_favorites_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle clearing all favorites"""
    await state.update_data(favorites=[])
    await callback.answer("All favorites cleared!")
    
    # Update the message to show empty favorites
    await callback.message.edit_text(
        "⭐ You don't have any favorite cryptocurrencies yet.\n\n"
        "To add favorites, search for a coin using the '🔍 Search Coin' button "
        "or view top cryptocurrencies, then select 'Add to Favorites'."
    )


def register_favorites_handlers(dp):
    """Register all favorites related handlers"""
    router = Router()
    
    # Button handler for "Favorites"
    router.message.register(favorites_command, F.text == "⭐ Favorites")
    
    # Callback handlers for favorite operations
    router.callback_query.register(add_favorite_callback, F.data.startswith("add_fav_"))
    router.callback_query.register(remove_favorite_callback, F.data.startswith("rm_fav_"))
    router.callback_query.register(clear_favorites_callback, F.data == "clear_favorites")
    
    dp.include_router(router)

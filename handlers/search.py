from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu import get_main_menu_keyboard
from services.coinlore_api import CoinloreAPI


class SearchStates(StatesGroup):
    waiting_for_query = State()


async def search_command(message: types.Message, state: FSMContext):
    """Handle the Search Coin button press"""
    await state.set_state(SearchStates.waiting_for_query)
    
    cancel_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Cancel")]],
        resize_keyboard=True
    )
    
    await message.answer(
        "Please enter the name or symbol of the cryptocurrency you want to search for:",
        reply_markup=cancel_keyboard
    )


async def cancel_search(message: types.Message, state: FSMContext):
    """Cancel the search operation and return to main menu"""
    await state.clear()
    await message.answer(
        "Search canceled. What would you like to do next?",
        reply_markup=get_main_menu_keyboard()
    )


async def process_search_query(message: types.Message, state: FSMContext):
    """Process the search query entered by the user"""
    query = message.text.strip().lower()
    
    # Search for the coin in the CoinLore API
    search_results = []
    
    # Get the first 100 coins
    coins_data = await CoinloreAPI.get_tickers(0, 100)
    
    # The API returns data in a nested structure where 'data' contains the coin list
    if coins_data and isinstance(coins_data, dict) and 'data' in coins_data:
        coins = coins_data['data']
    elif coins_data and isinstance(coins_data, list):
        coins = coins_data
    else:
        coins = []
    
    if coins:
        # Filter coins by name or symbol
        for coin in coins:
            # Check if coin is a dictionary before using get()
            if not isinstance(coin, dict):
                continue
                
            name = coin.get('name', '').lower()
            symbol = coin.get('symbol', '').lower()
            nameid = coin.get('nameid', '').lower()
            
            if (query in name or query in symbol or query in nameid):
                search_results.append(coin)
        
        # Limit to top 5 results
        search_results = search_results[:5]
    
    if search_results:
        result_text = "🔍 Search Results:\n\n"
        
        # Create inline buttons for each result
        buttons = []
        for coin in search_results:
            coin_id = coin.get('id')
            coin_name = coin.get('name')
            coin_symbol = coin.get('symbol')
            coin_price = coin.get('price_usd', 'N/A')
            
            result_text += f"*{coin_name} ({coin_symbol})*\n"
            result_text += f"Price: ${coin_price}\n"
            result_text += f"Rank: {coin.get('rank', 'N/A')}\n\n"
            
            # Add button for this coin
            buttons.append([InlineKeyboardButton(
                text=f"{coin_name} ({coin_symbol})",
                callback_data=f"coin_{coin_id}"
            )])
        
        # Add a keyboard with buttons for each result
        if buttons:
            result_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            
            await message.answer(
                result_text,
                reply_markup=result_keyboard,
                parse_mode="Markdown"
            )
            
            # Return to main menu
            await state.clear()
            await message.answer(
                "What would you like to do next?",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await state.clear()
            await message.answer(
                "No results found. Please try a different search term.",
                reply_markup=get_main_menu_keyboard()
            )
    else:
        await state.clear()
        await message.answer(
            "No results found or error connecting to the API. Please try again later.",
            reply_markup=get_main_menu_keyboard()
        )


def register_search_handlers(dp):
    """Register all search related handlers"""
    router = Router()
    
    # Button handler for "Search Coin"
    router.message.register(search_command, F.text == "🔍 Search Coin")
    
    # Cancel search
    router.message.register(cancel_search, SearchStates.waiting_for_query, F.text == "🔙 Cancel")
    
    # Process search query
    router.message.register(process_search_query, SearchStates.waiting_for_query)
    
    dp.include_router(router)
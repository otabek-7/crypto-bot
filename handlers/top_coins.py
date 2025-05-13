from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.coinlore_api import CoinloreAPI
from keyboards.coin_buttons import get_top_coins_keyboard
from keyboards.main_menu import get_main_menu_keyboard, get_coin_menu_inline_keyboard


# Define states for pagination
class TopCoinsStates(StatesGroup):
    viewing_list = State()
    viewing_coin = State()
    page = State()


async def top_cryptos_handler(message: types.Message, state: FSMContext):
    """
    Handler for the Top Cryptos button.
    Shows a list of top cryptocurrencies with pagination.
    """
    # Show typing status while fetching data
    await message.chat.do("typing")
    
    # Reset state data and set the page to 0
    await state.update_data(page=0)
    await state.set_state(TopCoinsStates.viewing_list)
    
    await show_top_coins_page(message, state)


async def show_top_coins_page(message: types.Message, state: FSMContext):
    """
    Display the current page of top cryptocurrencies.
    """
    # Get current page from state
    state_data = await state.get_data()
    page = state_data.get('page', 0)
    
    # Calculate start index for API pagination (10 coins per page)
    start = page * 10
    
    # Fetch data from the API
    coins_data = await CoinloreAPI.get_tickers(start=start, limit=10)
    
    if not coins_data or 'data' not in coins_data or not coins_data['data']:
        await message.answer(
            "❌ Sorry, couldn't fetch cryptocurrency data. Please try again later.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    coins = coins_data['data']
    
    # Create a message with the list of coins
    header_text = f"💹 *Top Cryptocurrencies* (Page {page + 1})\n\n"
    
    await message.answer(
        header_text, 
        parse_mode="Markdown",
        reply_markup=get_top_coins_keyboard(coins)
    )


async def coin_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Handler for coin selection from the list.
    Shows detailed information about a selected cryptocurrency.
    """
    # Extract coin ID from callback data
    coin_id = callback_query.data.split('_')[1]
    
    # Switch to viewing specific coin state
    await state.set_state(TopCoinsStates.viewing_coin)
    await state.update_data(selected_coin_id=coin_id)
    
    # Acknowledge the callback
    await callback_query.answer()
    
    # Show typing status while fetching data
    await callback_query.message.chat.do("typing")
    
    # Fetch coin data
    coin_data = await CoinloreAPI.get_ticker(coin_id)
    
    if not coin_data:
        await callback_query.message.answer(
            "❌ Sorry, couldn't fetch data for this cryptocurrency. Please try again later."
        )
        return
    
    # Format coin information
    coin_name = coin_data.get('name', 'Unknown')
    coin_symbol = coin_data.get('symbol', '?')
    price_usd = float(coin_data.get('price_usd', 0))
    price_btc = float(coin_data.get('price_btc', 0))
    market_cap = float(coin_data.get('market_cap_usd', 0))
    volume_24h = float(coin_data.get('volume24', 0))
    percent_change_1h = coin_data.get('percent_change_1h', '0')
    percent_change_24h = coin_data.get('percent_change_24h', '0')
    percent_change_7d = coin_data.get('percent_change_7d', '0')
    
    # Add emoji based on price change
    emoji_24h = "🔴" if float(percent_change_24h) < 0 else "🟢"
    
    coin_text = (
        f"{emoji_24h} *{coin_name} ({coin_symbol})*\n\n"
        f"💵 *Price:* ${price_usd:.4f} USD / {price_btc:.8f} BTC\n"
        f"💰 *Market Cap:* ${format_large_number(market_cap)} USD\n"
        f"📊 *Volume (24h):* ${format_large_number(volume_24h)} USD\n\n"
        f"⏱ *Change (1h):* {percent_change_1h}%\n"
        f"📅 *Change (24h):* {percent_change_24h}%\n"
        f"📆 *Change (7d):* {percent_change_7d}%\n"
    )
    
    # Save coin name for later use in other handlers
    await state.update_data(selected_coin_name=coin_name)
    
    await callback_query.message.answer(
        coin_text,
        parse_mode="Markdown",
        reply_markup=get_coin_menu_inline_keyboard()
    )


async def pagination_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Handler for pagination navigation.
    """
    action = callback_query.data
    state_data = await state.get_data()
    current_page = state_data.get('page', 0)
    
    if action == "prev_coins" and current_page > 0:
        await state.update_data(page=current_page - 1)
    elif action == "next_coins":
        await state.update_data(page=current_page + 1)
    
    # Acknowledge the callback
    await callback_query.answer()
    
    # Update the message with new page
    await show_top_coins_page(callback_query.message, state)


def format_large_number(num: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"


def register_top_coins_handlers(dp):
    """
    Register handlers for top cryptocurrencies functionality
    """
    router = Router()
    
    # Message handlers
    router.message.register(top_cryptos_handler, F.text == "💹 Top Cryptos")
    
    # Callback handlers
    router.callback_query.register(
        coin_callback_handler,
        F.data.startswith('coin_'),
        TopCoinsStates.viewing_list
    )
    
    router.callback_query.register(
        pagination_callback_handler,
        F.data.in_(["prev_coins", "next_coins"]),
        TopCoinsStates.viewing_list
    )
    
    dp.include_router(router)
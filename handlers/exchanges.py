from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from keyboards.main_menu import get_main_menu_keyboard
from services.coinlore_api import CoinloreAPI


async def exchanges_command(message: types.Message, state: FSMContext):
    """Handle the Exchanges button press"""
    
    # Get exchange data from CoinLore API
    exchanges_data = await CoinloreAPI.get_exchanges()
    
    # Debug logging to understand the API response
    logging.info(f"Exchange API response type: {type(exchanges_data)}")
    if exchanges_data:
        logging.info(f"Exchange data sample: {str(exchanges_data)[:200]}")
    else:
        logging.error("Exchange API returned None")
    
    # Handle different response formats
    if isinstance(exchanges_data, dict):
        if 'data' in exchanges_data:
            # Format: {"data": [...exchanges...]}
            exchanges = exchanges_data['data']
            logging.info(f"Extracted exchange data from 'data' field, got {len(exchanges)} exchanges")
        else:
            # Format: {"1": {...}, "2": {...}} - ID-keyed dictionary
            exchanges = list(exchanges_data.values())
            logging.info(f"Extracted exchange data from dictionary values, got {len(exchanges)} exchanges")
    elif isinstance(exchanges_data, list):
        # Format: [...exchanges...]
        exchanges = exchanges_data
        logging.info(f"Exchange data is already a list, got {len(exchanges)} exchanges")
    else:
        exchanges = []
        logging.error(f"Could not extract exchange data from response: {exchanges_data}")
    
    if exchanges and len(exchanges) > 0:
        # Filter out non-dictionary items
        valid_exchanges = [ex for ex in exchanges if isinstance(ex, dict)]
        logging.info(f"Found {len(valid_exchanges)} valid exchange entries out of {len(exchanges)}")
        
        # Handle empty results after filtering
        if not valid_exchanges:
            logging.error("No valid exchange entries found after filtering")
            await message.answer(
                "Unable to retrieve exchange data at this time. Please try again later.",
                reply_markup=get_main_menu_keyboard()
            )
            return
            
        # Sort exchanges by volume - safely handle possible string values or missing keys
        def get_volume(exchange):
            try:
                volume = exchange.get('volume_usd', 0)
                return float(volume) if volume else 0
            except (ValueError, TypeError):
                logging.warning(f"Invalid volume value for exchange: {exchange.get('name', 'Unknown')}")
                return 0
                
        sorted_exchanges = sorted(valid_exchanges, key=get_volume, reverse=True)
        
        # Take top 10 exchanges
        top_exchanges = sorted_exchanges[:10]
        
        # Format the message with exchange information
        message_text = "📊 Top Cryptocurrency Exchanges by Volume\n\n"
        
        # Create inline buttons for exchanges
        buttons = []
        
        for exchange in top_exchanges:
            name = exchange.get('name', 'Unknown')
            
            # Safely parse volume
            try:
                volume = float(exchange.get('volume_usd', 0))
                volume_formatted = f"${volume:,.2f}" if volume else "N/A"
            except (ValueError, TypeError):
                logging.warning(f"Could not format volume for exchange: {name}")
                volume_formatted = "N/A"
                
            # Get pairs count - handle both 'pairs' and 'active_pairs' keys
            pairs = exchange.get('pairs', exchange.get('active_pairs', 'N/A'))
            
            message_text += f"*{name}*\n"
            message_text += f"Volume (24h): {volume_formatted}\n"
            message_text += f"Trading Pairs: {pairs}\n\n"
            
            # Add button for this exchange - create safe URL
            name_id = exchange.get('name_id', name.lower().replace(' ', '-'))
            exchange_url = f"https://www.coinlore.com/exchange/{name_id}"
            buttons.append([InlineKeyboardButton(
                text=name,
                url=exchange_url
            )])
        
        # Create keyboard with buttons
        exchange_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.answer(
            message_text,
            reply_markup=exchange_keyboard,
            parse_mode="Markdown"
        )
        
        # Return to main menu
        await message.answer(
            "What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        logging.error(f"No exchanges data returned from API: {exchanges_data}")
        await message.answer(
            "Unable to retrieve exchange data at this time. Please try again later.",
            reply_markup=get_main_menu_keyboard()
        )


def register_exchanges_handlers(dp):
    """Register all exchanges related handlers"""
    router = Router()
    
    # Button handler for "Exchanges"
    router.message.register(exchanges_command, F.text == "📊 Exchanges")
    
    dp.include_router(router)
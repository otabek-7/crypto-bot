from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_top_coins_keyboard(coins: List[Dict[Any, Any]]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with buttons for top cryptocurrencies.
    
    Args:
        coins: List of coin data dictionaries from API
        
    Returns:
        InlineKeyboardMarkup: Keyboard with coin buttons
    """
    buttons = []
    
    for coin in coins[:10]:  # Limit to top 10 coins
        coin_name = coin.get('name', 'Unknown')
        coin_symbol = coin.get('symbol', '?')
        coin_id = coin.get('id', '')
        price_usd = coin.get('price_usd', '0.00')
        price_change = coin.get('percent_change_24h', '0.00')
        
        # Add emoji based on price change
        emoji = "🔴" if float(price_change) < 0 else "🟢"
        
        button_text = f"{emoji} {coin_name} ({coin_symbol}): ${float(price_usd):.2f} ({price_change}%)"
        buttons.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=f"coin_{coin_id}"
        )])
    
    # Add navigation buttons
    navigation_row = [
        InlineKeyboardButton(text="⬅️ Previous", callback_data="prev_coins"),
        InlineKeyboardButton(text="Next ➡️", callback_data="next_coins")
    ]
    buttons.append(navigation_row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_exchange_keyboard(exchanges: List[Dict[Any, Any]]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with buttons for cryptocurrency exchanges.
    
    Args:
        exchanges: List of exchange data dictionaries from API
        
    Returns:
        InlineKeyboardMarkup: Keyboard with exchange buttons
    """
    buttons = []
    
    for exchange in exchanges[:10]:  # Limit to 10 exchanges
        exchange_name = exchange.get('name', 'Unknown')
        exchange_id = exchange.get('id', '')
        volume_usd = exchange.get('volume_usd', '0')
        
        # Format volume with K, M, B for better readability
        volume_formatted = format_large_number(float(volume_usd))
        
        button_text = f"🏛️ {exchange_name}: ${volume_formatted} 24h Vol"
        buttons.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=f"exchange_{exchange_id}"
        )])
    
    # Add navigation buttons
    navigation_row = [
        InlineKeyboardButton(text="⬅️ Previous", callback_data="prev_exchanges"),
        InlineKeyboardButton(text="Next ➡️", callback_data="next_exchanges")
    ]
    buttons.append(navigation_row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_coin_markets_keyboard(markets: List[Dict[Any, Any]], coin_name: str) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard with buttons for markets trading a specific cryptocurrency.
    
    Args:
        markets: List of market data dictionaries from API
        coin_name: Name of the cryptocurrency
        
    Returns:
        InlineKeyboardMarkup: Keyboard with market buttons
    """
    buttons = []
    
    for market in markets[:8]:  # Limit to 8 markets
        exchange_name = market.get('name', 'Unknown')
        pair = market.get('pair', '?')
        price_usd = market.get('price_usd', '0.00')
        
        button_text = f"💱 {exchange_name}: {pair} ${float(price_usd):.2f}"
        buttons.append([InlineKeyboardButton(
            text=button_text, 
            callback_data=f"market_{market.get('id', '')}"
        )])
    
    # Add navigation and back buttons
    navigation_row = [
        InlineKeyboardButton(text="⬅️ Previous", callback_data="prev_markets"),
        InlineKeyboardButton(text="Next ➡️", callback_data="next_markets")
    ]
    buttons.append(navigation_row)
    
    buttons.append([InlineKeyboardButton(text=f"🔙 Back to {coin_name}", callback_data="back_to_coin")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_large_number(num: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        num: Number to format
        
    Returns:
        String representation with appropriate suffix
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return f"{num:.2f}"
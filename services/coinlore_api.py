import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union


class CoinloreAPI:
    """Service for interacting with Coinlore cryptocurrency API."""
    
    # Updated to the correct API URL
    BASE_URL = "https://api.coinlore.com"
    
    @staticmethod
    async def _make_request(endpoint: str) -> Union[Dict, List, None]:
        """Make an asynchronous request to the Coinlore API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Response data as dictionary, list or None if error occurred
        """
        url = f"{CoinloreAPI.BASE_URL}{endpoint}"
        try:
            logging.info(f"Making API request to: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            # Attempt to parse JSON regardless of Content-Type
                            result = await response.json(content_type=None)
                            logging.info(f"API response successful, content type: {response.content_type}")
                            return result
                        except Exception as e:
                            # If parsing fails, log it and return None
                            logging.error(f"Failed to parse JSON from {url}: {str(e)}")
                            
                            # Debug: Log the response content
                            text = await response.text()
                            logging.debug(f"Response content: {text[:200]}...")  # Log first 200 chars
                            
                            return None
                    else:
                        logging.error(f"API request failed: {url}, status: {response.status}")
                        return None
        except Exception as e:
            logging.error(f"Error making API request to {url}: {str(e)}")
            return None
    
    @classmethod
    async def get_global_stats(cls) -> Optional[List]:
        """Get global cryptocurrency statistics.
        
        Returns:
            List of global market statistics or None if error occurred
        """
        return await cls._make_request("/api/global/")
    
    @classmethod
    async def get_tickers(cls, start: int = 0, limit: int = 100) -> Optional[List]:
        """Get information about multiple cryptocurrencies.
        
        Args:
            start: Offset for pagination
            limit: Number of results to return (max 100)
            
        Returns:
            List of cryptocurrency data dictionaries or None if error occurred
        """
        return await cls._make_request(f"/api/tickers/?start={start}&limit={limit}")
    
    @classmethod
    async def get_ticker(cls, coin_id: str) -> Optional[Dict]:
        """Get information about a specific cryptocurrency.
        
        Args:
            coin_id: ID of the cryptocurrency
            
        Returns:
            Dictionary with cryptocurrency data or None if error occurred
        """
        result = await cls._make_request(f"/api/ticker/?id={coin_id}")
        return result[0] if result and isinstance(result, list) and len(result) > 0 else None
    
    @classmethod
    async def get_coin_markets(cls, coin_id: str) -> Optional[List]:
        """Get top 50 markets for a specific cryptocurrency.
        
        Args:
            coin_id: ID of the cryptocurrency
            
        Returns:
            List of market data dictionaries or None if error occurred
        """
        return await cls._make_request(f"/api/coin/markets/?id={coin_id}")
    
    @classmethod
    async def get_exchanges(cls) -> Optional[List]:
        """Get a list of all exchanges on the platform.
        
        Returns:
            List of exchange data dictionaries or None if error occurred
        """
        # Corrected endpoint - the correct endpoint is /api/exchanges/ (plural)
        return await cls._make_request("/api/exchanges/")
    
    @classmethod
    async def get_exchange(cls, exchange_id: str) -> Optional[Dict]:
        """Get information about a specific exchange.
        
        Args:
            exchange_id: ID of the exchange
            
        Returns:
            Dictionary with exchange data or None if error occurred
        """
        return await cls._make_request(f"/api/exchange/?id={exchange_id}")
    
    @classmethod
    async def get_coin_social_stats(cls, coin_id: str) -> Optional[Dict]:
        """Get social media statistics for a specific cryptocurrency.
        
        Args:
            coin_id: ID of the cryptocurrency
            
        Returns:
            Dictionary with social statistics or None if error occurred
        """
        return await cls._make_request(f"/api/coin/social_stats/?id={coin_id}")
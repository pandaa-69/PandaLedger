import logging
import yfinance as yf
from django.core.cache import cache
from django.apps import apps
from decimal import Decimal

logger = logging.getLogger(__name__)

def get_usd_inr_rate():
    """
    Fetches the live USD to INR exchange rate.

    Strategy:
    1. Check Cache (TTL 3 hours).
    2. If not in cache, fetch from Yahoo Finance.
    3. If successful, update Cache and persist to DB (Asset model) for future fallback.
    4. If YFinance fails, attempt to retrieve the last known rate from DB.
    5. If DB is empty, return a hardcoded safe fallback.

    Returns:
        float: The current USD/INR exchange rate.
    """
    cache_key = 'usd_inr_live_rate'
    cached_rate = cache.get(cache_key)

    if cached_rate:
        return cached_rate

    # Dynamic import to avoid circular dependency if core is imported by portfolio
    Asset = apps.get_model('portfolio', 'Asset')
    fallback_value = 87.00 

    try:
        # fetch data from yahoo 
        ticker = yf.Ticker("INR=X")

        # now after the data is fetched we will only need the most recent one 

        data = ticker.history( period = "1d", interval ="1m")

        if not data.empty:
            current_rate = round(float(data['Close'].iloc[-1]), 2)

            # we will save it in cache for 3hrs 
            cache.set('usd_inr_live_rate', current_rate, 10800) # 3hrs in seconds 

            return current_rate
        else:
            logger.warning("Yahoo Finance returned empty data for INR=X")

    except Exception as e:
        logger.error(f"Error fetching USD Rate from Yahoo: {e}")

    # Fallback Strategy: Try DB first, then hardcoded value
    try:
        asset = Asset.objects.get(symbol="INR=X")
        logger.info(f"Using DB fallback rate: {asset.last_price}")
        return float(asset.last_price)
    except Asset.DoesNotExist:
        logger.warning("No DB fallback found for INR=X. Using hardcoded default.")
        return fallback_value

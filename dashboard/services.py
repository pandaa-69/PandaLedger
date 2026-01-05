import logging
import yfinance as yf
import random
import threading
from django.core.cache import cache
from .models import MarketCache

logger = logging.getLogger(__name__)

def fetch_live_data_and_save():
    """
    Fetches real-time market data from Yahoo Finance and caches it.
    
    Operations:
    1. Fetches prices for Indices, Gold/Silver, Crypto, and Forex.
    2. Fetches relevant financial news.
    3. Saves consolidated JSON to Redis (TTL 10 mins) and Database (Permanent).
    
    This function is designed to be run in a background thread to avoid blocking requests.
    """
    logger.info("Background Update: Fetching fresh market data...")
    
    tickers_config = {
        "indices": { "nifty":"^NSEI", "sensex":"^BSESN", 'nasdaq':"^IXIC" },
        "commodities": { "gold":"GC=F", "silver":"SI=F" },
        "crypto": { "bitcoin":"BTC-USD", "eth":"ETH-USD" },
        "forex": { "usd_inr":"INR=X" }
    }

    dashboard_data = { "market_summary": [], "news": [] }

    try:
        # 1. Fetch USD Rate for Currency Conversions
        usd_ticker = yf.Ticker("INR=X")
        # Fallback to history if fast_info fails or is empty
        try:
            usd_price = usd_ticker.fast_info.last_price
        except:
             usd_price = 87.0 # Safe fallback

        # 2. Fetch Assets
        for category, items in tickers_config.items():
            for name, symbol in items.items():
                try:
                    ticker = yf.Ticker(symbol)
                    # Fetch 5 days to ensure we have a previous close even after weekends/holidays
                    history = ticker.history(period="5d", interval="1d")

                    if not history.empty:
                        current_price = float(history['Close'].iloc[-1])

                        # Gold/Silver Conversion Logic (Ounce USD -> 10g INR/1kg INR)
                        if name == "gold":
                            # Convert 1 Troy Ounce USD -> 10 Grams INR
                            current_price = (current_price * usd_price / 31.1035) * 10
                            history['Close'] = (history["Close"] * usd_price / 31.1035) * 10
                        elif name == "silver":
                            # Convert 1 Troy Ounce USD -> 1 Kg INR
                            conversion_factor = 1000 
                            current_price = (current_price * usd_price / 31.1035) * conversion_factor
                            history['Close'] = (history["Close"] * usd_price / 31.1035) * conversion_factor
                        
                        # Calculate Change %
                        if len(history) > 1:
                            prev_close = float(history['Close'].iloc[-2])
                        else:
                            prev_close = current_price
                        
                        if prev_close > 0:
                            change_pct = ((current_price - prev_close) / prev_close) * 100
                        else:
                            change_pct = 0.0

                        dashboard_data["market_summary"].append({
                            "id": name,
                            "category": category,
                            "symbol": symbol,
                            "price": round(current_price, 2),
                            "change": round(change_pct, 2),
                            "graph_data": history['Close'].tolist()
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch market data for {name} ({symbol}): {e}")

        # 3. Fetch News
        news_sources = ["^NSEI", "^IXIC"] 
        raw_articles = []

        for src in news_sources:
            try:
                t = yf.Ticker(src)
                src_news = t.news
                tag = "India" if src == "^NSEI" else "Global"
                for article in src_news:
                    article['source_tag'] = tag
                raw_articles.extend(src_news)
            except Exception as e:
                logger.warning(f"News fetch error for {src}: {e}")

        random.shuffle(raw_articles)

        # Normalize News Data
        for item in raw_articles[:6]:
            content = item.get('content', {})
            thumbnail = content.get('thumbnail', {})
            
            # Fallback for thumbnail location variations
            if not thumbnail: 
                thumbnail = item.get('thumbnail', {})
            
            image_url = None
            if thumbnail and 'resolutions' in thumbnail:
                resolutions = thumbnail['resolutions']
                if resolutions: 
                    image_url = resolutions[0]['url']
            
            click_info = content.get('clickThroughUrl')
            link = click_info.get('url') if click_info else "#"
            provider_info = content.get('provider')
            publisher = provider_info.get('displayName') if provider_info else "Yahoo Finance"
            title = content.get('title')

            if title:
                dashboard_data["news"].append({
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "tag": item.get('source_tag', 'Global'),
                    "image": image_url,
                    "time": content.get('pubDate'),
                })

        # --- SAVE TO DB & CACHE ---
        # 1. Update Cache (Fast Access) - 10 minutes TTL
        cache.set('market_dashboard_full', dashboard_data, 600)
        
        # 2. Persist to DB (Reliability)
        MarketCache.objects.update_or_create(id=1, defaults={'data': dashboard_data})
        logger.info("Market Data Successfully Updated & Saved to DB")
        
        return dashboard_data

    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}", exc_info=True)
        return {"error": str(e)}

def get_market_dashboard_data():
    """
    Retrieves market dashboard data with a multi-tiered caching strategy.
    
    Strategy:
    1. RAM (Redis Cache): Returns instantly (< 10ms).
    2. DB (Persistent Cache): Returns if cache misses (< 50ms), then triggers background refresh.
    3. Cold Start: Fetches fresh data synchronously if both Cache and DB are empty (Fallback).
    
    Returns:
        dict: The dashboard data JSON.
    """
    # 1. TRY RAM CACHE
    cached_data = cache.get("market_dashboard_full")
    if cached_data:
        return cached_data
    
    # 2. TRY DATABASE
    db_data = MarketCache.objects.filter(id=1).first()
    if db_data:
        logger.info("Serving stale data from DB. Triggering background update...")
        
        # Trigger background update for NEXT time
        thread = threading.Thread(target=fetch_live_data_and_save, daemon=True)
        thread.start()
        
        return db_data.data

    # 3. COLD START
    logger.info("Cold Start: Fetching fresh data synchronously...")
    return fetch_live_data_and_save()

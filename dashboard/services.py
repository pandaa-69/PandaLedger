import logging
import yfinance as yf
import random
import threading
from django.core.cache import cache
from .models import MarketCache

logger = logging.getLogger(__name__)

def fetch_live_data_and_save():
    """
    Fetches real-time market data from Yahoo Finance using optimized batch processing.
    
    Operations:
    1. Batch fetches prices for Indices, Commodities, Crypto, and Forex (1 API Call).
    2. Fetches/Caches financial news separately (10-minute TTL to reduce load).
    3. Saves consolidated JSON to Redis (5s TTL) and Database.
    
    This function leverages batching to maintain a 5-second update interval safely within rate limits.
    """
    logger.info("Background Update: Fetching fresh market data via Batch API...")
    
    tickers_config = {
        "indices": { "nifty":"^NSEI", "sensex":"^BSESN", 'nasdaq':"^IXIC" },
        "commodities": { "gold":"GC=F", "silver":"SI=F" },
        "crypto": { "bitcoin":"BTC-USD", "eth":"ETH-USD" },
        "forex": { "usd_inr":"INR=X" }
    }

    # Flatten symbols for batch request
    all_symbols = []
    for category in tickers_config.values():
        all_symbols.extend(category.values())
    
    # Add currency ticker if not present (it is in forex, but good to ensure uniqueness)
    all_symbols = list(set(all_symbols))
    
    dashboard_data = { "market_summary": [], "news": [] }

    try:
        # 1. Batch Fetch All Prices (Efficient: 1 Call)
        # Using threads=True for faster downloading; group_by='ticker' organizes data by symbol
        market_data = yf.download(tickers=" ".join(all_symbols), period="5d", interval="1d", group_by='ticker', threads=True, progress=False, auto_adjust=True)
        print(market_data.to_json())
        # Extract USD Rate for Conversions
        # Handle potential missing data for INR=X
        usd_price = 87.0
        if 'INR=X' in market_data.columns:
            try:
                usd_hist = market_data['INR=X']
                if not usd_hist.empty:
                    usd_price = float(usd_hist['Close'].iloc[-1])
            except Exception:
                pass # Keep default 87.0

        # 2. Process Assets
        for category, items in tickers_config.items():
            for name, symbol in items.items():
                try:
                    # Check if symbol data exists in the batch response
                    if symbol not in market_data.columns:
                        continue
                        
                    ticker_df = market_data[symbol]
                    
                    if not ticker_df.empty:
                        # Extract Close Series and handle NaNs
                        close_data = ticker_df['Close'].dropna()
                        if close_data.empty:
                            continue

                        current_price = float(close_data.iloc[-1])
                        display_history = close_data.copy()

                        # Gold/Silver Conversions (USD -> INR)
                        if name == "gold":
                            # 1 Troy Ounce USD -> 10 Grams INR
                            current_price = (current_price * usd_price / 31.1035) * 10
                            display_history = (display_history * usd_price / 31.1035) * 10
                        elif name == "silver":
                            # 1 Troy Ounce USD -> 1 Kg INR
                            current_price = (current_price * usd_price / 31.1035) * 1000
                            display_history = (display_history * usd_price / 31.1035) * 1000
                        
                        # Change Calculation
                        if len(display_history) > 1:
                            prev_close = float(display_history.iloc[-2])
                        else:
                            prev_close = current_price

                        change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0.0

                        dashboard_data["market_summary"].append({
                            "id": name,
                            "category": category,
                            "symbol": symbol,
                            "price": round(current_price, 2),
                            "change": round(change_pct, 2),
                            "graph_data": display_history.tolist()
                        })
                except Exception as e:
                    logger.warning(f"Error processing {name} in batch: {e}")

        # 3. Fetch News (Cached for 10 mins)
        cached_news = cache.get('market_news_items')
        
        if cached_news:
            dashboard_data["news"] = cached_news
        else:
            # Fetch fresh news only if cache expired
            news_sources = ["^NSEI", "^IXIC"] 
            raw_articles = []
            
            for src in news_sources:
                try:
                    # News fetch still requires Ticker object access
                    t = yf.Ticker(src)
                    src_news = t.news
                    tag = "India" if src == "^NSEI" else "Global"
                    for article in src_news:
                        article['source_tag'] = tag
                    raw_articles.extend(src_news)
                except Exception as e:
                    logger.warning(f"News fetch error for {src}: {e}")

            if raw_articles:
                random.shuffle(raw_articles)
                processed_news = []
                for item in raw_articles[:6]:
                    content = item.get('content', {})
                    thumbnail = content.get('thumbnail', {})
                    # Fallback for thumbnail location variations
                    if not thumbnail: thumbnail = item.get('thumbnail', {})
                    
                    image_url = None
                    if thumbnail and 'resolutions' in thumbnail:
                         r = thumbnail['resolutions']
                         if r: image_url = r[0]['url']
                    
                    click_info = content.get('clickThroughUrl')
                    link = click_info.get('url') if click_info else "#"
                    provider_info = content.get('provider')
                    publisher = provider_info.get('displayName') if provider_info else "Yahoo Finance"
                    title = content.get('title')
                    
                    if title:
                        processed_news.append({
                            "title": title,
                            "publisher": publisher,
                            "link": link,
                            "tag": item.get('source_tag', 'Global'),
                            "image": image_url,
                            "time": content.get('pubDate')
                        })
                
                dashboard_data["news"] = processed_news
                # Cache News specifically for 10 minutes (600 seconds)
                cache.set('market_news_items', processed_news, 600)

        # --- SAVE TO DB & CACHE ---
        # Cache for 10 seconds to match user's desired update rate
        cache.set('market_dashboard_full', dashboard_data, 10)
        
        # Persist to DB
        MarketCache.objects.update_or_create(id=1, defaults={'data': dashboard_data})
        logger.info(f"Market Data Updated. News Cached: {bool(cached_news)}")
        
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
        #  Only trigger update if one isn't already running
        if not cache.get("market_update_lock"):
            logger.info("Serving stale data from DB. Triggering background update...")
            
            # Set a temporary lock 5 seconds to prevent multiple threads from spawning 
            # if 100 users hit this exact line simultaneously.
            cache.set("market_update_lock", "true", 5)
            
            thread = threading.Thread(target=fetch_live_data_and_save, daemon=True)
            thread.start()
        else:
            logger.info("Serving stale data from DB. Update already in progress (Locked).")
        
        return db_data.data

    # 3. COLD START
    logger.info("Cold Start: Fetching fresh data synchronously...")
    return fetch_live_data_and_save()

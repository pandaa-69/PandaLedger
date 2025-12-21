import yfinance as yf
import random
import threading
from django.core.cache import cache
from .models import MarketCache # Import the new model

def fetch_live_data_and_save():
    """
    This function does the heavy lifting (Yahoo API calls).
    It saves the result to DB and Cache.
    """
    print("🔄 Background Update: Fetching fresh market data...")
    
    tickers_config = {
        "indices": { "nifty":"^NSEI", "sensex":"^BSESN", 'nasdaq':"^IXIC" },
        "commodities": { "gold":"GC=F", "silver":"SI=F" },
        "crypto": { "bitcoin":"BTC-USD", "eth":"ETH-USD" },
        "forex": { "usd_inr":"INR=X" }
    }

    dashboard_data = { "market_summary": [], "news": [] }

    try:
        # 1. Fetch USD Rate
        usd_ticker = yf.Ticker("INR=X")
        usd_price = usd_ticker.fast_info.last_price 
        
        # 2. Fetch Assets
        for category, items in tickers_config.items():
            for name, symbol in items.items():
                try:
                    ticker = yf.Ticker(symbol)
                    history = ticker.history(period="5d", interval="1d")

                    if not history.empty:
                        current_price = history['Close'].iloc[-1]

                        # Gold/Silver Conversion Logic
                        if name == "gold":
                            current_price = (current_price * usd_price / 31.1035) * 10
                            history['Close'] = (history["Close"] * usd_price / 31.1035) * 10
                        elif name == "silver":
                            conversion_factor = 1000 
                            current_price = (current_price * usd_price / 31.1035) * conversion_factor
                            history['Close'] = (history["Close"] * usd_price / 31.1035) * conversion_factor
                        
                        # Calculate Change %
                        if len(history) > 1:
                            prev_close = history['Close'].iloc[-2]
                        else:
                            prev_close = current_price
                        
                        change_pct = ((current_price - prev_close) / prev_close) * 100

                        dashboard_data["market_summary"].append({
                            "id": name,
                            "category": category,
                            "symbol": symbol,
                            "price": round(current_price, 2),
                            "change": round(change_pct, 2),
                            "graph_data": history['Close'].tolist()
                        })
                except Exception as e:
                    print(f"Failed to fetch {name}: {e}")

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
                print(f"News error {src}: {e}")

        random.shuffle(raw_articles)

        for item in raw_articles[:6]:
            content = item.get('content', {})
            thumbnail = content.get('thumbnail', {})
            if not thumbnail: thumbnail = item.get('thumbnail', {})
            
            image_url = None
            if thumbnail and 'resolutions' in thumbnail:
                resolutions = thumbnail['resolutions']
                if resolutions: image_url = resolutions[0]['url']
            
            click_info = content.get('clickThroughUrl')
            link = click_info.get('url') if click_info else "#"
            provider_info = content.get('provider')
            publisher = provider_info.get('displayName') if provider_info else "Yahoo"
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
        # 1. Cache for Speed (10 mins)
        cache.set('market_dashboard_full', dashboard_data, 60)
        
        # 2. DB for Backup (Permanent until next update)
        # We use update_or_create to ensure we only ever have 1 row
        obj, created = MarketCache.objects.update_or_create(id=1, defaults={'data': dashboard_data})
        print("✅ Market Data Updated & Saved to DB")
        
        return dashboard_data

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return {"error": str(e)}

def get_market_dashboard_data():
    """
    The main service function called by the View.
    Implements: RAM -> DB -> Background Fetch
    """
    # 1. TRY RAM CACHE (Fastest: < 10ms) ⚡
    cached_data = cache.get("market_dashboard_full")
    if cached_data:
        return cached_data
    
    # 2. TRY DATABASE (Fast: < 50ms) 💾
    db_data = MarketCache.objects.filter(id=1).first()
    if db_data:
        # We have data, but it wasn't in cache (maybe cache expired).
        # Return this data INSTANTLY so user doesn't wait.
        print("⚡ Serving from DB (Stale), Triggering Background Update...")
        
        # Trigger background update for NEXT time
        thread = threading.Thread(target=fetch_live_data_and_save)
        thread.start()
        
        return db_data.data

    # 3. COLD START (Slow: 2-3s) 🐢
    # If no Cache AND no DB (First run ever), we must wait.
    print("🐢 Cold Start: Fetching synchronously...")
    return fetch_live_data_and_save()
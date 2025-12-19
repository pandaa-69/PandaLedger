import yfinance as yf , random
from django.core.cache import cache
def get_market_dashboard_data():
    cached_data = cache.get("market_dashboard_full")
    if cached_data:
        return cached_data
    
    tickers_config = {
        "indices":{
            "nifty":"^NSEI",
            "sensex":"^BSESN",
            'nasdaq':"^IXIC",
        },
        "commodities":{
            "gold":"GC=F",
            "silver":"SI=F"
        },
        "crypto":{
            "bitcoin":"BTC-USD",
            "eth":"ETH-USD",
        },
        "forex":{
            "usd_inr":"INR=X"
        }
    }

    dashboard_data ={
        "market_summary":[],
        "news":[]
    }

    try:
        # pre fetching the usd rate so we can use it for gold calulation
        usd_ticker = yf.Ticker("INR=X")
        # we want just the lastest current price so i think we should use fast_info rather than history()

        usd_price = usd_ticker.fast_info.last_price 
        
        # Fetching the prices and graphs
        for category, items in tickers_config.items():
            for name, symbol in items.items():
                try:
                    ticker = yf.Ticker(symbol)

                    # getting the 5 days history for the graph 
                    history = ticker.history(period="5d", interval="1d")

                    if not history.empty:
                        current_price = history['Close'].iloc[-1]

                        # Gold rate conversion form usd / ounce tp rupees / 10g

                        if name=="gold":
                            # to remmeber the formula i am righting it here (Price_usd * USD_rate/31.1035)*10
                            current_price = (current_price*usd_price/31.1035)*10
                            # we need to change the rate for the graph to for showing it correctly

                            history['Close'] = (history["Close"]*usd_price/31.1035)*10
                        elif name == "silver":
                            # Silver: Convert USD/oz -> INR/1kg (Standard Indian Rate)
                            conversion_factor = 1000 
                            # Formula: (Price_USD * USD_Rate / 31.1035) * 1000
                            current_price = (current_price * usd_price / 31.1035) * conversion_factor
                            history['Close'] = (history["Close"] * usd_price / 31.1035) * conversion_factor
                        # calculating the change percentage 
                        # if only 1 day of the data exists
                        if len(history)>1:
                            prev_close = history['Close'].iloc[-2]
                        else:
                            prev_close = current_price
                        
                        change_pct = ((current_price-prev_close)/ prev_close)*100

                        dashboard_data["market_summary"].append({
                            "id": name,
                            "category": category,
                            "symbol": symbol,
                            "price": round(current_price, 2),
                            "change": round(change_pct, 2),
                            "graph_data": history['Close'].tolist() # Points for the line chart
                        })
                except Exception as e :
                    print(f"Failed to fetch {name}: {e}")

        # --- B. FETCH TOP MARKET NEWS (Mixed Sources) ---
        # We fetch news from Nifty (India) and Nasdaq (Global)
        news_sources = ["^NSEI", "^IXIC"] 
        raw_articles = []

        for src in news_sources:
            try:
                t = yf.Ticker(src)
                # Add source tag so we know where it came from
                src_news = t.news
                tag = "India" if src =="^NSEI" else "Global"
                for article in src_news:
                    article['source_tag'] = tag
                raw_articles.extend(src_news)
            except Exception as e:
                print(f"News error {src}: {e}")

        # Shuffle them so you get a mix of India + Global news
        random.shuffle(raw_articles)

        # Process top 6 articles
        for item in raw_articles[:6]:
        
            # Safely extract image (Yahoo API structure varies)
            
            content = item.get('content', {})

            # getting the image
            image_url = None # i will handle it in frontend
            thumbnail = content.get('thumbnail', {})
            if not thumbnail:
                # fallback just in case if we dont found an img thant check the outer
                thumbnail = item.get('thumbnail', {})

            if thumbnail  and 'resolutions' in thumbnail:
                resolutions = thumbnail['resolutions']
                if resolutions:
                    image_url = resolutions[0]['url']
            
            # get the link 
            click_info = content.get('clickThroughUrl')
            link = click_info.get('url') if click_info else "#"

            # get the news provider
            provider_info = content.get('provider')
            publisher = provider_info.get('displayName') if provider_info else "Yahoo"

            # only add title if we found one 
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

        # 3. Cache the result for 10 minutes
        cache.set('market_dashboard_full', dashboard_data, 600)
        
        return dashboard_data

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return {"error": str(e)}


    

    
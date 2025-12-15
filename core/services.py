import yfinance as yf 
from django.core.cache import cache

def get_usd_inr_rate():
    """ Fetches the live USD to INR rate
    """
    #we will use caching so that we dont hit yahoo website multiple times to get banned 

    # we will check if there is any data in the cache if yes we will simple return the data ans if not then we will try to fetch it from yfinance

    # check if the rate is already in our Cache 
    cached_rate = cache.get('usd_inr_live_rate')

    if cached_rate:
        return cached_rate
    
    # if not in cache fetch it from the internet 
    
    try:
        # fetch data from yahoo 
        ticker = yf.Ticker("INR=X")

        # now after the data is fetched we will only need the most recent one 

        data = ticker.history( period = "1d", interval ="1m")

        if not data.empty:
            current_rate = round(data['Close'].iloc[-1], 2)

            # we will save it in cache for 3hrs 
            cache.set('usd_inr_live_rate', current_rate, 10800) # 3hrs in seconds 

            return current_rate
    except Exception as e:
        print(f"Error fetching USD Rate: {e}")
        # if internet is down we will return a safe fallback value 

        return 87.00
    
    return 87.00 # Fallback if data is empty i will improve it later with the help of DB 
        

    


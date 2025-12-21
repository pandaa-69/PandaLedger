import numpy as np
import pandas as pd
import yfinance as yf
from django.core.cache import cache
from analytics.models import PortfolioSnapshot
from portfolio.models import Holding

def fetch_benchmark_data(days=365):
    """
    Fetches Nifty 50 (^NSEI) data for the last year and caches it.
    """
    cache_key = f"market_benchmark_nifty_{days}"
    data = cache.get(cache_key)
    
    if data is None:
        try:
            ticker = yf.Ticker("^NSEI")
            hist = ticker.history(period=f"{days}d")
            
            # 👇 FIX 1: Strip Timezone from Market Data
            hist.index = hist.index.tz_localize(None) 
            
            # Calculate Daily Returns (% change from yesterday)
            hist['Market_Return'] = hist['Close'].pct_change()
            data = hist['Market_Return'].dropna()
            
            cache.set(cache_key, data, 60*60*24) # Cache for 24 hours
        except Exception as e:
            print(f"Error fetching benchmark: {e}")
            return pd.Series(dtype=float) 
        
    return data

def calculate_portfolio_metrics(user):
    """
    Calculates Real Volatility and Beta based on user's snapshot history.
    """
    # 1. Get User's Daily History from DB
    snapshots = PortfolioSnapshot.objects.filter(user=user).order_by('date')
    
    if not snapshots.exists() or len(snapshots) < 10:
        return {
            "beta": 0,
            "volatility": "Low", 
            "volatility_num": 0
        }

    # 2. Prepare DataFrame
    df = pd.DataFrame(list(snapshots.values('date', 'total_value')))
    
    # Convert Decimal to Float immediately
    df['total_value'] = df['total_value'].astype(float) 
    
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # 👇 FIX 2: Strip Timezone from Portfolio Data
    df.index = df.index.tz_localize(None)

    # 3. Calculate Daily Returns
    df['Portfolio_Return'] = df['total_value'].pct_change().dropna()
    
    # --- CALCULATION 1: VOLATILITY (Risk) ---
    if len(df) > 1:
        daily_std = df['Portfolio_Return'].std()
        annualized_volatility = daily_std * np.sqrt(252) * 100 
    else:
        annualized_volatility = 0
    
    volatility_label = "Low"
    if annualized_volatility > 15: volatility_label = "Medium"
    if annualized_volatility > 30: volatility_label = "High"

    # --- CALCULATION 2: BETA (Market Sensitivity) ---
    market_returns = fetch_benchmark_data()
    
    # Align dates (Now safe because both are timezone-naive!)
    aligned_data = pd.concat([df['Portfolio_Return'], market_returns], axis=1).dropna()
    aligned_data.columns = ['Portfolio', 'Market']
    
    if len(aligned_data) > 10:
        covariance = aligned_data.cov().iloc[0, 1]
        market_variance = aligned_data['Market'].var()
        if market_variance > 0:
            beta = covariance / market_variance
        else:
            beta = 0
    else:
        beta = 0

    return {
        "beta": round(beta, 2),
        "volatility": volatility_label,
        "volatility_num": round(annualized_volatility, 2)
    }

def calculate_health_score(user):
    """
    Generates a score (0-100) based on diversification logic.
    """
    holdings = list(Holding.objects.filter(user=user).select_related('asset'))
    if not holdings:
        return 50 

    score = 100
    penalties = []
    
    # Calculate total value safely
    total_value = sum(float(h.current_value()) for h in holdings)
    
    if total_value == 0: return 0

    # 1. Concentration Risk
    for h in holdings:
        weight = float(h.current_value()) / total_value
        if weight > 0.40:
            score -= 15
            penalties.append(f"High concentration in {h.asset.symbol}")

    # 2. Sector Diversification
    sectors = set(h.asset.sector for h in holdings if h.asset.sector)
    if len(sectors) < 3:
        score -= 20
        penalties.append("Poor sector diversity")

    # 3. Asset Class Diversification
    types = set(h.asset.asset_type for h in holdings)
    if len(types) < 2:
        score -= 10
        penalties.append("Lack of multi-asset allocation")

    return max(score, 0)